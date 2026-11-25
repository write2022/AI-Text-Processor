# import pymysql


import os
import psycopg

#dict_row 是 psycopg3 内置的行工厂函数，来自 psycopg.rows 子模块，不是你自己写的，也不是第三方库。
from psycopg.rows import dict_row

#DSN 是连接字符串
PG_DSN = os.environ.get(
    "PG_DSN",
    "postgresql://postgres:postgres@localhost:5432/postgres"
)


#qihang postgre oracle
# 1. 提取一个获取连接的公共方法，方便复用
# def get_conn():
#     # return pymysql.connect(
#     #     host='localhost',
#     #     user='root',
#     #     password='123456',
#     #     database='ai_chat_system',
#     #     charset='utf8mb4'
#     # )
#     # 改动：优先读环境变量，没有就默认localhost（适配你原来本地Navicat）
#
#
#     host = os.getenv("DB_HOST", "localhost")
#     user = os.getenv("DB_USER", "root")
#     password = os.getenv("DB_PASSWORD", "123456")
#     database = os.getenv("DB_NAME", "ai_chat_system")
#     return pymysql.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=database,
#         charset='utf8mb4'
#     )

PG_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS translate_task (
    task_id TEXT PRIMARY KEY,
    source_text TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    result TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
)
"""

PG_INSERT_TASK_SQL = """
    INSERT INTO translate_task (task_id, source_text, target_lang)
    VALUES (%s, %s, %s)
    ON CONFLICT (task_id) DO NOTHING
"""

#成功和失败用两条独立 UPDATE 而非单条带 COALESCE 的语句，因为 COALESCE 只能保留原值、无法清空字段——重试成功时必须显式清除上一次的 error，否则会留下 status=done 但 error 有值的矛盾数据
PG_MARK_DONE_SQL = """
    UPDATE translate_task
    SET result = %s, status = 'done', error = NULL, finished_at = now()
    WHERE task_id = %s
"""
PG_MARK_FAILED_SQL = """
    UPDATE translate_task
    SET error = %s, status = 'failed', finished_at = now()
    WHERE task_id = %s
"""
#def get_task_by_id(task_id)
PG_GET_TASK_SQL = """
SELECT task_id, source_text, target_lang, result, status, error, created_at, finished_at
FROM translate_task
WHERE task_id = %s
"""



def get_pg_conn():
    return psycopg.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "123456"),
        dbname=os.getenv("PG_DB", "ai_project"),
        # PG_DSN,
        row_factory=dict_row,
    )

def create_pg_table():
    #get_pg_conn() 这一句自己就会抛异常（容器没起、密码错、驱动没装）。没有这行，finally 里 conn.close() 会撞上 NameError: name 'conn' is not defined——真正的错误被这个次生错误盖掉了，你排障时会看到一条完全无关的报错，非常坑。这是 try/finally 配资源变量的固定写法。
    conn=None
    try:
        conn=get_pg_conn()
        with conn.transaction():
            conn.execute(PG_CREATE_TABLE_SQL)
        #验证
        print("translate_task 建表完成")
    except psycopg.Error as e:
        print("PG建表失败:",e)
        #这是启动自检入口。建表失败意味着后面所有 DAO 全会炸——如果你只 print 然后继续跑，接下来 create_pending_task 会抛一串"表不存在"的第二现场报错，你会去查翻译逻辑，其实问题在第一步。让异常冒出去，程序停在真正的失败点。
        raise
    finally:
        if conn is not None:
            conn.close()


# 2. 建表方法
# def create_table():
#     conn = get_conn()
#     cursor = conn.cursor()
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS messages (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         user_input TEXT NOT NULL,
#         ai_reply TEXT NOT NULL,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)
#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("表建好了，去 Navicat 刷新看看")

#"登记一个刚开始的任务"，它的语义被写死在名字里：状态必然是 pending，结果必然是空。让调用方能传 status，就等于允许出现"任务还没跑，状态已经是 done"这种自相矛盾的数据
def create_pending_task(task_id, source_text, target_lang):
    conn = None
    try:
        conn = get_pg_conn()
        with conn.transaction():
            cur = conn.execute(PG_INSERT_TASK_SQL, (task_id, source_text, target_lang))
            return cur.rowcount
    except psycopg.Error:
        raise
    finally:
        if conn is not None:
            conn.close()

def save_task_result(task_id, result=None, error=None):
    if (result is None) == (error is None):
        raise ValueError("result 和 error 必须且只能传一个")
    conn = None
    try:
        conn = get_pg_conn()
        with conn.transaction():
            if error is None:
                cur = conn.execute(PG_MARK_DONE_SQL, (result, task_id))
            else:
                cur = conn.execute(PG_MARK_FAILED_SQL, (error, task_id))
            return cur.rowcount
    except psycopg.Error:
        raise
    finally:
        if conn is not None:
            conn.close()

#查询函数
def get_task_by_id(task_id):
    conn = None
    try:
        conn = get_pg_conn()
        with conn.transaction():
            cur = conn.execute(PG_GET_TASK_SQL, (task_id,))
            row = cur.fetchone()
        return row
    except psycopg.Error:
        raise
    finally:
        if conn is not None:
            conn.close()


# 3. 保存聊天记录的方法（把用户的话和 AI 的话存进去）
# def save_message(user_text, ai_text):
#     conn = get_conn()
#     cursor = conn.cursor()
#     sql = "INSERT INTO messages (user_input, ai_reply) VALUES (%s, %s)"
#     cursor.execute(sql, (user_text, ai_text))
#     conn.commit()
#     cursor.close()
#     conn.close()

# 4. create_table,读取历史记录的方法
# def get_history():
#     conn = get_conn()
#     cursor = conn.cursor()
#     sql = "SELECT user_input, ai_reply, created_at FROM messages ORDER BY id DESC"
#     cursor.execute(sql)
#     results = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return results

if __name__ == "__main__":

    create_pg_table()
    # create_table()
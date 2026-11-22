import pymysql
import os


#qihang postgre oracle
# 1. 提取一个获取连接的公共方法，方便复用
def get_conn():
    # return pymysql.connect(
    #     host='localhost',
    #     user='root',
    #     password='123456',
    #     database='ai_chat_system',
    #     charset='utf8mb4'
    # )
    # 改动：优先读环境变量，没有就默认localhost（适配你原来本地Navicat）
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "123456")
    database = os.getenv("DB_NAME", "ai_chat_system")
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )


# 2. 建表方法
def create_table():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_input TEXT NOT NULL,
        ai_reply TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("表建好了，去 Navicat 刷新看看")

# 3. 保存聊天记录的方法（把用户的话和 AI 的话存进去）
def save_message(user_text, ai_text):
    conn = get_conn()
    cursor = conn.cursor()
    sql = "INSERT INTO messages (user_input, ai_reply) VALUES (%s, %s)"
    cursor.execute(sql, (user_text, ai_text))
    conn.commit()
    cursor.close()
    conn.close()

# 4. 读取历史记录的方法
def get_history():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "SELECT user_input, ai_reply, created_at FROM messages ORDER BY id DESC"
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
if __name__ == "__main__":
    create_table()
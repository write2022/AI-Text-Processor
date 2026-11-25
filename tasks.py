import threading
import queue
import time


from api_client import translate_text
# from database import save_message

import json
import pika
from database import save_task_result

# ── 拓扑命名
EXCHANGE         = "translate.exchange"
QUEUE            = "translate.queue"
DEAD_EXCHANGE    = "translate.dlx"
DEAD_QUEUE       = "translate.dead"
ROUTING_KEY      = "translate"
DEAD_ROUTING_KEY = "translate.dead"

# task_queue = queue.Queue()
#
# def worker():
#     while True:
#         item = task_queue.get()
#
#         try:
#             ai_text=translate_text(item)
#
#             save_message(item,ai_text)
#
#             # task_queue.task_done()
#         except Exception as e:
#             print("报错",e)
#         finally:
#             task_queue.task_done()



# 启动工作线程。
# threading.Thread(target=worker, daemon=True).start()
#
# # 向工作线程发送三十个任务请求。
# for item in range(30):
#     task_queue.put(item)
#
# # 阻塞直到所有任务完成。
# task_queue.join()
# print('All work completed')

# threading.Thread(target=worker, daemon=True).start()

# ── 连接
credentials = pika.PlainCredentials(username='guest', password='guest')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", credentials=credentials)
)
#链路是：账号 → connection → channel
channel = connection.channel()
#connection	一条真正的 TCP 连接	重，建/断代价大
#channel	在这条 TCP 上"多路复用"出来的虚拟通道	轻，随便开随便关


# ── 声明顺序：先死信通道，再业务队列
channel.exchange_declare(exchange=DEAD_EXCHANGE, exchange_type="direct", durable=True)
channel.queue_declare(queue=DEAD_QUEUE, durable=True)
channel.queue_bind(exchange=DEAD_EXCHANGE, queue=DEAD_QUEUE, routing_key=DEAD_ROUTING_KEY)

channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
channel.queue_declare(
    queue=QUEUE, durable=True,
    arguments={
        "x-dead-letter-exchange": DEAD_EXCHANGE,
        "x-dead-letter-routing-key": DEAD_ROUTING_KEY,   # ← 必须写，别走隐式
    },
)
channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

# ── 一次只取一条：处理完 ack 前不再塞下一条 ─────────────
channel.basic_qos(prefetch_count=1)

# ── 回调：翻译 + 落库 + ack/nack ───────────────────────
def on_message(ch, method, properties, body):
    print(f">>> 收到: {body}", flush=True)
    data = json.loads(body)
    task_id = data["task_id"]
    try:
        result = translate_text(data["source_text"])   # 成功路径
        print(f">>> 成功: {task_id} -> {result}", flush=True)
        save_task_result(task_id, result=result)        # 先落库标 done
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 再 ack
    except Exception as e:

        import traceback; traceback.print_exc()
        print(f">>> 失败: {task_id} -> {e}", flush=True)
        save_task_result(task_id, error=str(e))         # 失败也先落库标 failed
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # 再进死信


print(f"监听队列: {QUEUE}", flush=True)
channel.basic_consume(queue=QUEUE, on_message_callback=on_message, auto_ack=False)
print("consumer ready, waiting...")
channel.start_consuming()
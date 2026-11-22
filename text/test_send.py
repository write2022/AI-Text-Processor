# test_send.py
import pika
import json
import uuid

RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'
VHOST = '/'
TASK_QUEUE = 'translate.task'

task_id = str(uuid.uuid4())
payload = {
    "task_id": task_id,
    "source_text": "你好，这是一条测试文本",
    "target_lang": "英文"
}

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    virtual_host=VHOST,
    credentials=credentials,
    heartbeat=600
)
conn = pika.BlockingConnection(params)
channel = conn.channel()
channel.queue_declare(queue=TASK_QUEUE, durable=True)

channel.basic_publish(
    exchange="",
    routing_key=TASK_QUEUE,
    body=json.dumps(payload),
    properties=pika.BasicProperties(delivery_mode=2)
)
conn.close()
print(f"消息发送成功，task_id={task_id}")

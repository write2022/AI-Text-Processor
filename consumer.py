import pika
import json


import requests

RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'
VHOST = '/'

EXCHANGE_NAME = 'translate.exchange'
TASK_QUEUE = 'translate.task'

DEEPSEEK_API_KEY = "sk-xxxxxx"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def translate(text, lang_code="English"):
    resp = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model":"deepseek-chat",
            "message":[
                    {
                        "role": "system",
                        "content": f"你是专业翻译引擎。把用户给的文本翻译成{target_lang}，只输出译文，不要任何解释、引号或markdown标记。",
                    },
                    {"role": "user", "content": text},
                ],
                "temperature": 0.3
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()



def callback(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    print("===== 收到翻译任务 =====")
    print(f"task_id: {data['task_id']}")
    print(f"原文：{data['source_text']}")
    print(f"目标语言：{data['target_lang']}")

    result = translate(data["source_text"], data["target_lang"])
    print(f"译文：{result}")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("已 ack\n")
    # # 后面这里可以加上调用翻译、写入PostgreSQL的逻辑
    # print("模拟翻译完成\n")
    #
    # # 确认消息消费成功
    # ch.basic_ack(delivery_tag=method.delivery_tag)

    #翻译




def main():
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

    channel.basic_qos(prefetch_count=1)

    channel.queue_declare(queue=TASK_QUEUE, durable=True)

    channel.basic_consume(queue=TASK_QUEUE, on_message_callback=callback)

    print("Worker 启动，等待任务...")
    channel.start_consuming()


if __name__ == '__main__':
    main()

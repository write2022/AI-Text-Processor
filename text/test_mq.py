import pika
import json
import uuid
from datetime import datetime, timezone

# ========== 配置（适配你现在的rabbitmq容器！） ==========
RABBITMQ_HOST = '127.0.0.1'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'
VHOST = '/'

# 交换机与队列命名
EXCHANGE_NAME = 'translate.exchange'
TASK_QUEUE = 'translate.task'
DLX_EXCHANGE = 'translate.dlx'
DLQ_QUEUE = 'translate.task.dlq'


def get_connection():
    """建立带认证的连接"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=VHOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    return pika.BlockingConnection(parameters)


def setup_topology(channel):
    """
    声明交换机、队列、绑定关系，以及死信队列
    幂等：重复执行不会报错（参数一致的前提下）
    """
    # 1. 业务交换机（direct 类型，按 routing_key 精确匹配）
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type='direct',
        durable=True,
    )

    # 2. 死信交换机
    channel.exchange_declare(
        exchange=DLX_EXCHANGE,
        exchange_type='direct',
        durable=True,
    )

    # 3. 死信队列
    channel.queue_declare(
        queue=DLQ_QUEUE,
        durable=True,
    )
    channel.queue_bind(
        queue=DLQ_QUEUE,
        exchange=DLX_EXCHANGE,
        routing_key='dead',
    )

    # 4. 主任务队列，配置死信路由
    channel.queue_declare(
        queue=TASK_QUEUE,
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLX_EXCHANGE,
            'x-dead-letter-routing-key': 'dead',
            # 'x-message-ttl': 300000,   # 5 分钟没被消费就进死信，按需开启
        }
    )
    channel.queue_bind(
        queue=TASK_QUEUE,
        exchange=EXCHANGE_NAME,
        routing_key='task',
    )


def publish_task(channel, source_text, source_lang='auto', target_lang='English'):
    """
    投递一个翻译任务
    返回 task_id，供后续查询状态
    """
    task_id = str(uuid.uuid4())

    # 消息体用 JSON，方便扩展字段
    message = {
        'task_id': task_id,
        'source_text': source_text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'retry_count': 0,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key='task',
        body=json.dumps(message, ensure_ascii=False),
        properties=pika.BasicProperties(
            delivery_mode=2,          # 消息持久化，RabbitMQ 重启不丢
            content_type='application/json',
            message_id=task_id,
        ),
    )
    print(f" [x] 已投递任务 task_id={task_id}")
    return task_id


def main():
    connection = get_connection()
    channel = connection.channel()

    # 声明拓扑（幂等，每次启动都可以调用）
    setup_topology(channel)

    # 发送测试任务
    test_text = "人工智能正在改变软件开发的方式。"
    task_id = publish_task(channel, source_text=test_text, target_lang='English')

    # 查看队列状态
    method = channel.queue_declare(queue=TASK_QUEUE, passive=True)
    print(f" [*] 队列 {TASK_QUEUE} 当前消息数: {method.method.message_count}")

    connection.close()
    print(f" [*] 完成。可访问 http://127.0.0.1:15672 查看队列 {TASK_QUEUE}")


if __name__ == '__main__':
    main()

# # import pika
# #
# # # 连接本地 Docker 里的 RabbitMQ
# # connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
# # channel = connection.channel()
# #
# # # 声明一个队列
# # channel.queue_declare(queue='hello')
# #
# # # 发送消息
# # channel.basic_publish(exchange='', routing_key='hello', body='Hello Docker RabbitMQ!')
# # print(" [x] 成功发送消息 'Hello Docker RabbitMQ!'")
# #
# # connection.close()import pika
# #
# # # 连接本地 Docker 里的 RabbitMQ
# # connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
# # channel = connection.channel()
# #
# # # 声明一个队列
# # channel.queue_declare(queue='hello')
# #
# # # 发送消息
# # channel.basic_publish(exchange='', routing_key='hello', body='Hello Docker RabbitMQ!')
# # print(" [x] 成功发送消息 'Hello Docker RabbitMQ!'")
# #
# # connection.close()
#
# """
# mq_producer_test.py
# RabbitMQ 生产者测试脚本
# 用途：验证任务投递链路，包含持久化、死信队列、路由配置
# """
#
# import pika
# import json
# import uuid
# from datetime import datetime, timezone
#
# # ========== 配置 ==========
# RABBITMQ_HOST = '127.0.0.1'
# RABBITMQ_PORT = 5672
# RABBITMQ_USER = 'app'          # 建议不用 guest，见下方说明
# RABBITMQ_PASS = 'your_password'
# VHOST = '/'
#
# # 交换机与队列命名
# EXCHANGE_NAME = 'translate.exchange'
# TASK_QUEUE = 'translate.task'
# DLX_EXCHANGE = 'translate.dlx'
# DLQ_QUEUE = 'translate.task.dlq'
#
#
# def get_connection():
#     """建立带认证的连接"""
#     credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#     parameters = pika.ConnectionParameters(
#         host=RABBITMQ_HOST,
#         port=RABBITMQ_PORT,
#         virtual_host=VHOST,
#         credentials=credentials,
#         heartbeat=600,           # 心跳，防止长连接被断开
#         blocked_connection_timeout=300,
#     )
#     return pika.BlockingConnection(parameters)
#
#
# def setup_topology(channel):
#     """
#     声明交换机、队列、绑定关系，以及死信队列
#     幂等：重复执行不会报错（参数一致的前提下）
#     """
#     # 1. 业务交换机（direct 类型，按 routing_key 精确匹配）
#     channel.exchange_declare(
#         exchange=EXCHANGE_NAME,
#         exchange_type='direct',
#         durable=True,
#     )
#
#     # 2. 死信交换机
#     channel.exchange_declare(
#         exchange=DLX_EXCHANGE,
#         exchange_type='direct',
#         durable=True,
#     )
#
#     # 3. 死信队列
#     channel.queue_declare(
#         queue=DLQ_QUEUE,
#         durable=True,
#     )
#     channel.queue_bind(
#         queue=DLQ_QUEUE,
#         exchange=DLX_EXCHANGE,
#         routing_key='dead',
#     )
#
#     # 4. 主任务队列，配置死信路由
#     #    x-dead-letter-exchange: 消息被拒绝(nack/reject)且 requeue=False 时，转发到这个交换机
#     #    x-message-ttl: 可选，消息在队列中的存活时间（毫秒），超时也会进死信
#     channel.queue_declare(
#         queue=TASK_QUEUE,
#         durable=True,
#         arguments={
#             'x-dead-letter-exchange': DLX_EXCHANGE,
#             'x-dead-letter-routing-key': 'dead',
#             # 'x-message-ttl': 300000,   # 5 分钟没被消费就进死信，按需开启
#         }
#     )
#     channel.queue_bind(
#         queue=TASK_QUEUE,
#         exchange=EXCHANGE_NAME,
#         routing_key='task',
#     )
#
#
# def publish_task(channel, source_text, source_lang='auto', target_lang='English'):
#     """
#     投递一个翻译任务
#     返回 task_id，供后续查询状态
#     """
#     task_id = str(uuid.uuid4())
#
#     # 消息体用 JSON，方便扩展字段
#     message = {
#         'task_id': task_id,
#         'source_text': source_text,
#         'source_lang': source_lang,
#         'target_lang': target_lang,
#         'retry_count': 0,
#         'created_at': datetime.now(timezone.utc).isoformat(),
#     }
#
#     channel.basic_publish(
#         exchange=EXCHANGE_NAME,
#         routing_key='task',
#         body=json.dumps(message, ensure_ascii=False),
#         properties=pika.BasicProperties(
#             delivery_mode=2,          # 关键：消息持久化，RabbitMQ 重启不丢
#             content_type='application/json',
#             message_id=task_id,       # 便于追踪和幂等去重
#         ),
#     )
#     print(f" [x] 已投递任务 task_id={task_id}")
#     return task_id
#
#
# def main():
#     connection = get_connection()
#     channel = connection.channel()
#
#     # 声明拓扑（幂等，每次启动都可以调用）
#     setup_topology(channel)
#
#     # 发送测试任务
#     test_text = "人工智能正在改变软件开发的方式。"
#     task_id = publish_task(channel, source_text=test_text, target_lang='English')
#
#     # 查看队列状态
#     method = channel.queue_declare(queue=TASK_QUEUE, passive=True)
#     print(f" [*] 队列 {TASK_QUEUE} 当前消息数: {method.method.message_count}")
#
#     connection.close()
#     print(f" [*] 完成。可访问 http://127.0.0.1:15672 查看队列 {TASK_QUEUE}")
#
#
# if __name__ == '__main__':
#     main()
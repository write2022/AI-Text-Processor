import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from api_client import translate_text
# from database import save_message, get_history, create_table
# from api_client import translate_text, ocr
from ocr import get_text

from flask import Flask, request, jsonify, send_from_directory

# from tasks import worker
# from tasks import task_queue

import json
import uuid
import pika
from pika.exceptions import AMQPError

from database import create_pending_task, save_task_result

app = Flask(__name__)
# 允许跨域，这样你的前端网页（无论跑在哪里）都能调用这个接口.来自包 `flask-cors`，**给你的 Flask 后端全局开启跨域
CORS(app)

#自动建好 MQ 的结构，这个就叫设置拓扑。
# 拓扑常量
EXCHANGE    = "translate.exchange"
ROUTING_KEY = "translate"

# credentials = pika.PlainCredentials("guest", "guest")
# connection  = pika.BlockingConnection(
#     pika.ConnectionParameters(host="localhost", credentials=credentials)
# )
# channel = connection.channel()
#
# channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)

# 每次启动服务时，顺便检查一下表在不在
# with app.app_context():
#     try:
#         create_table()
#     except Exception as e:
#         print("建表失败，请检查数据库连接:", e)


# 接口 1：接收前端发来的文字，调 AI，存数据库，返回结果
# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     user_text = data.get('text', '')
#
#     if not user_text:
#         return jsonify({"error": "内容不能为空"}), 400
#
#     print(f"收到前端消息：{user_text}")
#
#     task_queue.put(user_text)

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_text = request.json.get("text")
#     if not user_text:
#         return jsonify({"error": "text required"}), 400
#
#     task_id = str(uuid.uuid4())
#
#     # ① 先落库，拿到 pending 记录
#     create_pending_task(task_id, user_text, target_lang="zh")
#
#     # ② 再投消息
#     channel.basic_publish(
#         exchange=EXCHANGE,
#         routing_key=ROUTING_KEY,
#         body=json.dumps({
#             "task_id": task_id,
#             "source_text": user_text,
#             "target_lang": "zh",
#         }).encode("utf-8"),
#         properties=pika.BasicProperties(delivery_mode=2),  # 2 = 持久化消息
#     )
#
#     # ③ 立刻返回，不等翻译
#     return jsonify({"task_id": task_id, "status": "pending"}), 202

def _publish(task_id: str, source_text: str, target_lang: str):
    params = pika.ConnectionParameters(
        host="localhost",
        credentials=pika.PlainCredentials("guest", "guest"),
        heartbeat=600,
        blocked_connection_timeout=300
    )
    conn = None
    try:
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        # 幂等声明，防止交换机不存在丢消息
        ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
        msg = {
            "task_id": task_id,
            "source_text": source_text,
            "target_lang": target_lang
        }
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=json.dumps(msg).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    finally:
        if conn is not None and conn.is_open:
            conn.close()

@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.json.get("text")
    if not user_text:
        return jsonify({"error": "text required"}), 400

    task_id = str(uuid.uuid4())
    # 第一步：落库pending
    create_pending_task(task_id, user_text, target_lang="zh")
    try:
        _publish(task_id, user_text, "zh")
    except AMQPError as e:
        # MQ投递失败，任务标记失败，防止消息凭空消失
        save_task_result(task_id, error=f"mq publish error: {str(e)}")
        return jsonify({"error": "fail to submit task to mq", "task_id": task_id}), 502

    return jsonify({"task_id": task_id, "status": "pending"}), 202



    # 1. 呼叫 AI（用的是你之前写的 api_client）
    # ai_text = translate_text(user_text)
    #
    # # 2. 存进数据库
    # save_message(user_text, ai_text)

    # 3. 返回给前端
    # return jsonify({"reply": "消息已进入后台队列，AI正在努力处理中，请稍后刷新查看。"})


# 新增：图片上传接口
# @app.route('/upload', methods=['POST'])
# def upload_image():
#     # 检查前端有没有传文件
#     if 'file' not in request.files:
#         return jsonify({"error": "没有找到上传的图片"}), 400
#
#     file = request.files['file']
#
#     # 把图片保存到本地临时文件夹
#     temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp.jpg")
#     file.save(temp_path)
#
#     # 1. 调用 OCR 提取文字
#     print("正在识别图片...")
#     ocr_text = ocr(temp_path)
#
#     if ocr_text == "没识别出文字":
#         return jsonify({"error": "图片里没有识别出文字"}), 400
#
#     # 2. 调用 API 翻译
#     print("正在翻译...")
#     ai_text = translate_text(ocr_text)
#
#     # 3. 存入数据库（存图片提取出的原文和翻译结果）
#     save_message(ocr_text, ai_text)
#
#     # 4. 返回给前端
#     return jsonify({"reply": ai_text})

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "没有找到上传的图片"}), 400

    file = request.files['file']
    temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp.jpg")
    file.save(temp_path)

    # 1. 调用 ocr.py 里的函数，拿到拆好行的元组 (比如 ('a', 'b', 'c'))
    ocr_lines = get_text(temp_path)

    if not ocr_lines:
        return jsonify({"error": "未识别出文字"}), 400

    # 2. 把拆好的行，用换行符连起来，交给 AI 翻译
    english_text = "\n".join(ocr_lines)

    print("正在翻译...")
    ai_text = translate_text(english_text)

    # 3. 存进数据库
    # save_message(english_text, ai_text)

    # 4. 返回给前端
    return jsonify({
        "reply": ai_text,
        # "lines": ocr_lines  # 顺便把拆分的行也发给前端
        "lines": list(ocr_lines)
    })

# 接口 2：获取历史记录
# @app.route('/history', methods=['GET'])
# def history():
#     records = get_history()
#     result = []
#     for row in records:
#         result.append({
#             "user": row[0],
#             "ai": row[1],
#             "time": str(row[2])
#         })
#     return jsonify(result)

# 托管前端静态页面
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# if __name__ == '__main__':
#     print("🚀 后端服务已启动！")
#     # 运行在 5000 端口
#     app.run(debug=True, port=5000)

if __name__ == "__main__":
    # debug=False 关闭reloader，根除子进程搞坏连接的问题
    app.run(host="127.0.0.1", port=5000, debug=False)
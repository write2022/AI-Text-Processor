from flask import Flask, request, jsonify
from flask_cors import CORS
from api_client import translate_text
from database import save_message, get_history, create_table

app = Flask(__name__)
# 允许跨域，这样你的前端网页（无论跑在哪里）都能调用这个接口
CORS(app)

# 每次启动服务时，顺便检查一下表在不在
with app.app_context():
    try:
        create_table()
    except Exception as e:
        print("建表失败，请检查数据库连接:", e)


# 接口 1：接收前端发来的文字，调 AI，存数据库，返回结果
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_text = data.get('text', '')

    if not user_text:
        return jsonify({"error": "内容不能为空"}), 400

    print(f"收到前端消息：{user_text}")

    # 1. 呼叫 AI（用的是你之前写的 api_client）
    ai_text = translate_text(user_text)

    # 2. 存进数据库
    save_message(user_text, ai_text)

    # 3. 返回给前端
    return jsonify({"reply": ai_text})


# 接口 2：获取历史记录
@app.route('/history', methods=['GET'])
def history():
    records = get_history()
    result = []
    for row in records:
        result.append({
            "user": row[0],
            "ai": row[1],
            "time": str(row[2])
        })
    return jsonify(result)


if __name__ == '__main__':
    print("🚀 后端服务已启动！")
    # 运行在 5000 端口
    app.run(debug=True, port=5000)
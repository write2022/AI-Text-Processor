import requests

def translate_text(text):
    api_key="sk-填入你的DeepSeekKey"
    url="https://api.deepseek.com/chat/completions"
    headers = {
        "content-type":"application/json",
        "Authorization":f"Bearer {api_key}"
    }

    data={
        "model":"deepseek-flash",
        "messages":[
            {"role":"system", "content":"你是一个专业的翻译助手。"},
            {"role": "user", "content": f"请把下面这段英文翻译成中文，只输出翻译结果：\n{text}"}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"网络请求出错：{e}"

if __name__ == "__main__":
    print("正在测试 api_client.py...")
    test_result = translate_text("Hello, this is a test.")
    print("测试结果：", test_result)

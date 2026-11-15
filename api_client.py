import requests
import json
from rapidocr import RapidOCR


# def ocr(image_path):
#     # 1. 启动引擎
#     engine = RapidOCR()
#     # 2. 识别图片
#     result = engine(image_path)
#
#     # 3. 判断有没有认出字
#     if result and result.txts:
#         # 把元组里的文字用空格拼成一整句话，然后交出去
#         return " ".join(result.txts)
#     else:
#         return "没识别出文字"

def translate_text(text):
    api_key="sk-填入你的DeepSeekKey"
    url="https://api.deepseek.com/chat/completions"
    headers = {
        "content-type":"application/json; charset=utf-8",
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
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"网络请求出错：{e}"



#测试

# if __name__ == "__main__":
#     print("正在测试 api_client.py...")
#     test_result = translate_text("Hello, this is a test.")
#     print("测试结果：", test_result)

# === 本地测试代码，只有直接运行这个文件时才会执行 ===
# if __name__ == "__main__":
#     print("=== 开始测试 OCR 功能 ===")
#
#     # 请确保你的文件夹里有一张叫 test.jpg 的图片（或者换成你实际图片的名字）
#     image_file = "1.jpg"
#
#     # 1. 测试 OCR 识别
#     english_text = ocr(image_file)
#     print(f"\n【OCR 识别结果】:\n{english_text}\n")
#
#     # 2. 测试调用 DeepSeek 翻译识别出来的英文
#     if english_text != "没识别出文字":
#         print("=== 开始测试翻译功能 ===")
#         chinese_text = translate_text(english_text)
#         print(f"\n【翻译结果】:\n{chinese_text}\n")
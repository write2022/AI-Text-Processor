import requests

# 1. 填入你刚刚在硅基流动创建的 Key
api_key = "sk-tbnzbbmhrakdztvqeuykrqqpnnthoiuyovdivdvpohywwqnu"
url = "https://api.siliconflow.cn/v1/embeddings"

# 2. 准备请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# 复用你刚才的 api_key、url 和 headers
def get_vector(text):
    data = {"model": "BAAI/bge-m3", "input": text}
    response = requests.post(url, headers=headers, json=data)
    return response.json()['data'][0]['embedding']

# 1. 获取三个句子的向量
vec1 = get_vector("今天天气真不错，我们去公园散步吧。")
vec2 = get_vector("阳光明媚，非常适合出门走走。")
vec3 = get_vector("这家火锅店的毛肚真好吃。")

# 2. 手搓余弦相似度
def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot_product / (norm_a * norm_b)

# 3. 打印对比结果
print(f"【天气】 vs 【阳光明媚】相似度: {cosine_similarity(vec1, vec2):.4f}")
print(f"【天气】 vs 【火锅】相似度: {cosine_similarity(vec1, vec3):.4f}")
# 3. 准备要转换的文字
data = {
    "model": "BAAI/bge-m3",  # 硅基流动免费提供的向量模型
    "input": "今天天气真不错，我们去公园散步吧。"
}

print("正在请求向量化 API...")
# 4. 发送请求
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    # 提取出那 1024 个数字组成的列表
    vector = result['data'][0]['embedding']

    print("✅ 成功获取向量！")
    print(f"这个向量的长度是: {len(vector)} 维")
    print(f"前 5 个数字长这样: {vector[:5]}")
else:
    print("❌ 出错了，状态码：", response.status_code)
    print(response.text)
from ocr import get_text

# 1. 指定你要测试的图片（改成你文件夹里真实的图片名）
img_path = "1.jpg"

print("开始调用 ocr.py 提取文字...")
lines = get_text(img_path)

# 2. 打印结果
if lines:
    print(f"\n✅ 识别成功！一共拆分出了 {len(lines)} 行文字：\n")
    for index, line in enumerate(lines):
        print(f"第 {index + 1} 行: {line}")
else:
    print("\n❌ 没有识别出任何文字。")
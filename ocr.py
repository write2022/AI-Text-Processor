# from rapidocr import RapidOCR
#
# engine = RapidOCR()
#
# img_url = "https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/master/resources/test_files/ch_en_num.jpg"
# result = engine(img_url)
# print(result)
#
# result.vis("vis_result.jpg")

#新
from rapidocr import RapidOCR

#老
# from rapidocr_onnxruntime import RapidOCR

def get_text(image_path):

# 初始化 OCR 引擎
    engine = RapidOCR()

# img_path = "ch_en_num.jpg"

# 2. 执行识别
# result = engine(img_path)
    result = engine(image_path)

# # 3. 打印原始结果
# print(result)
#
# print(result.txts)


    if result and result.txts:
        # 直接返回拆好行的元组/列表
        return result.txts
    else:
        return ()
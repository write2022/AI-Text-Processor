import os
import requests

from api_client import translate_text

# x = os.path.abspath("c:spam") 文档
a=os.path.dirname(os.path.abspath(__file__))
b=os.path.join(a,"test.txt")
c=os.path.join(a,"test1.txt")

# with open("test.txt") as d:
#    e = d.read()
#
# with open("test1.txt") as f:
#     f.write(e)

# with open(b,"r",encoding="gb2312") as d:
#     e=d.read()
# with open(c,"w",encoding="gb2312") as f:
#     f.write(e)


# b = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.txt")
#
# # 1. 先用 exists 探个路
# if os.path.exists(b):
#     # 如果文件存在（True），就正常读
#     print("文件存在，开始读取...")
#     with open(b, "r", encoding="utf-8") as f:
#         e = f.read()
# else:
#     # 如果文件不存在（False），就建一个
#     print("文件不存在，正在自动创建...")
#     with open(b, "w", encoding="utf-8") as f:
#         f.write("这是自动创建的新文件")
#         e = "这是自动创建的新文件"

try:
    # with open(b, "r", encoding="gb2312") as d:
    #     e = d.read()
    # with open(c, "w", encoding="gb2312") as f:
    #     f.write(e)
    # 尝试去读
    with open(b, "r", encoding="utf-8") as d:
        e = d.read()

    chinese=translate_text(e)


    # 读到了，再写
    with open(c, "w", encoding="utf-8") as f:
        f.write(chinese)
    print("成功！")
except FileNotFoundError:
    with open(b,"r",encoding="utf-8") as f:
        f.write("")
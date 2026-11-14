import os

# current_file_path = os.path.dirname(os.path.realpath(__file__))
# # sys.path.append(os.path.join(current_file_path, '..'))
# current_dir = os.path.dirname(current_file_path)
# file_path=os.path.join(current_dir,"test.txt")
#
# print(file_path)

##

# 1. 获取当前文件的真实绝对路径，砍掉文件名，留下所在文件夹（只砍一次！）
current_dir = os.path.dirname(os.path.realpath(__file__))
print("找到的文件夹是：", current_dir)

# 2. 拼接出 test.txt 的完整路径
file_path = os.path.join(current_dir, "test.txt")
print("准备写入的文件是：", file_path)

# 3. 核心步骤：打开文件，执行写入！(没有这三行，文件是不会出现的)
with open(file_path, mode="w", encoding="gb2312") as f:
    f.write("Hello AI! 我终于靠自己查文档，把中文写进文件里啦！\n")
    f.write("接下来，我要去接入 DeepSeek 的 API 了。")

print("✅ 执行完毕！请去上面的文件夹里找找 test.txt 吧！")
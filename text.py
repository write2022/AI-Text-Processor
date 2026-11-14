from database import save_message, get_history

# 存一条数据
save_message("你好，数据库通了！", "太棒了，我们马上做全栈！")
print("写入完成")

# 读出来看看
print("\n--- 历史记录 ---")
for row in get_history():
    print(f"用户: {row[0]} | AI: {row[1]}")

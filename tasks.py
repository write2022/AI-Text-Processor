import threading
import queue
import time

from api_client import translate_text
from database import save_message

task_queue = queue.Queue()

def worker():
    while True:
        item = task_queue.get()

        try:
            ai_text=translate_text(item)

            save_message(item,ai_text)

            # task_queue.task_done()
        except Exception as e:
            print("报错",e)
        finally:
            task_queue.task_done()



# 启动工作线程。
# threading.Thread(target=worker, daemon=True).start()
#
# # 向工作线程发送三十个任务请求。
# for item in range(30):
#     task_queue.put(item)
#
# # 阻塞直到所有任务完成。
# task_queue.join()
# print('All work completed')

threading.Thread(target=worker, daemon=True).start()
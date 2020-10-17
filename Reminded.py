import psutil
import time
from tkinter import *
import tkinter.messagebox


def checkProcess():
    procs = []
    for proc in psutil.process_iter():
        try:
            procInfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            procs.append(procInfo.get('name'))
            #print(procInfo)
    return 'wfica32.exe' in procs


# pyinstaller -F -w .py 打包成一个没有命令行窗口的可执行文件
if __name__ == '__main__':
    startTime = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f'begin check, at {startTime}')

    tk = Tk()
    tk.title("警告！！！")
    # 窗体大小
    tk.geometry('800x600')
    # 固定窗体
    tk.resizable(True, True)
    # 去除tk的默认弹框
    tk.withdraw()
    # 窗口置顶
    tk.wm_attributes('-topmost', 1)
    # 每30s检查一次进程是否存在
    wait_time = 30
    while True:
        flag = checkProcess()
        print(f'check process at {time.strftime("%Y-%m-%d %H:%M:%S")}, isExists: {flag}')
        # 进程不存在提醒
        if not flag:
            tkinter.messagebox.showinfo('警告', "云桌面掉了")
            wait_time = 60
            # 提醒后每60s检查一次进程是否存在
            while True:
                time.sleep(wait_time)
                flag = checkProcess()
                print(f'remind process at {time.strftime("%Y-%m-%d %H:%M:%S")}, isExists: {flag}')
                if not flag:
                    tkinter.messagebox.showinfo('警告', "快登录云桌面")
                else:
                    # 检测到了以后重新1分钟检测一次
                    break
        time.sleep(wait_time)

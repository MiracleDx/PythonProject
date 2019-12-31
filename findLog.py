# -*_ coding:utf8 -*-

import os
import glob
import datetime

# 定义异常
class noLogError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


# 切换到落盘目录
os.chdir('/var/log')
# 获取当前路径
sys_path = os.getcwd()
# 查找当前目录所有log文件
logs = glob.glob("*.log")

# 是否报错标志位
flag = False

for i in range(len(logs)):
	# 组装og文件路径
	file_path = sys_path + '/' + logs[i]
	# 获取文件元数据
	file_stat = os.stat(file_path)

	#print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file_path))))
	#print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path))))


	# 文件修改时间
	modifiedTime = datetime.datetime.fromtimestamp(file_stat.st_mtime)
	# 文件创建时间
	#createdTime = datetime.datetime.fromtimestamp(file_stat.st_ctime)

	# 获取当前时间
	now = datetime.datetime.now()
	# 获取当天00点
	zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)

	# 修改时间 <= 当前时间 && 修改时间 >= 00点
	if modifiedTime.__le__(now) and modifiedTime.__ge__(zeroToday):
		flag = True
		print(str.format('file:{}, modifiedTime:{}', logs[i], modifiedTime))

# 报错
if not flag:
	raise noLogError('Today is not generator log files')

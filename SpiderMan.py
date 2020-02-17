# !/usr/bin/env python
# coding=utf-8
'''
@Author: Dongx
@Description: 
@Date: 2020-02-06 09:13:34
@LastEditors: Dongx
@LastEditTime: 2020-02-17 15:07:57
'''

import requests
import time
import json
import re
import os
import shutil
import queue
from threading import Thread, current_thread
import sys
import random

# 蜘蛛侠
class SpiderMan(object):
    
    # 初始化
    def __init__(self):
        self.headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
                            "Host": "www.zhihu.com",
                            "Referer": "https://www.zhihu.com/",
                        }
        # 建立session
        self.session = requests.Session()
        self.session.keep_alive = False
    
    # 下载图片
    def download_jpg(self, image_url, image_localpath):
        response = requests.get(image_url, stream=True)
        if (response.status_code == 200):
            with open(image_localpath, 'wb') as f:
                response.raw.deconde_content = True
                shutil.copyfileobj(response.raw, f)

    # 获取回答
    def getAnswer(self, questionId):
        # 每次取10条回答
        limit = 10
        # 获取答案时的偏移量
        offset = 0
        # 开始时假设当前有这么多的回答
        total = 2 * limit
        # 我们当前已记录的回答数量
        record_num = 0
        # 标题
        title = questionId

        # 获取本地路径
        dir = os.path.abspath(local_path)
        # 获取图片的正则
        image_pattern = re.compile(r'<img.*?actualsrc="(https.*?.jpg)".*?/>', re.S)

        # 获取队列
        global queue
        print(f"开始下载问题： {title}...")
        while record_num < total:
            # 请求
            url = 'https://www.zhihu.com/api/v4/questions/' + questionId + '/answers?sort_by=default&include=data[*].is_normal,voteup_count,content&limit=' + str(limit) + '&offset=' + str(offset)
            response = self.session.get(url, headers=self.headers, timeout=10)
            response = json.loads(response.content)

            # 获取总回答数
            total = response['paging']['totals']
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f'{now} --- {title}的总回答数：{total}， 当前读取偏移量：{offset}， 剩余：{total - offset}， 当前队列空余容量：{100000 - queue.qsize()}')

            # 获取实体信息
            datas = response['data']

            if datas is not None:
                if total <= 0:
                    break;
            
            for data in datas:
                # 标题 替换掉非法字符
                title = data['question']['title'].replace("?", "？")
                # 作者名称 
                author = data['author']['name']
                answer = data['content']

                print(f'读取用户：{author}')

                # 获取图片链接
                results = re.findall(image_pattern, answer)
                for imgUrl in results:
                    # 获取文件名
                    filename = os.path.basename(imgUrl)
                    # 组装下载路径
                    imgPath = os.path.join(dir, title)
                    imgPath = os.path.join(imgPath, author)
                    # 判断文件夹是否存在
                    if not os.path.exists(imgPath):
                        os.makedirs(imgPath) 
                    #print(f'开始下载：{imgUrl}')
                    filePath = os.path.join(imgPath, filename)

                    # 生产数据
                    queue.put({'imgUrl': imgUrl, 'filePath': filePath, 'title': title, 'author': author})
                    # 下载
                    # self.download_jpg(imgUrl, filePath)

            # 请求的向后偏移量
            offset += len(datas)
            record_num += len(datas)

            # 随机沉睡1-3s
            time.sleep(random.choice([1, 2, 3]))
            # 如果获取的数组size小于limit,循环结束
            if len(datas) < limit:
                break
        print(f"问题：{title} 下载完毕...")
        dones.append(title)

# 生产者
class Producer(Thread):

    def __init__(self, func, args, name=""):
        Thread.__init__(self)
        self.func = func
        self.args = args
        self.name = name

    def run(self):
        print(self.name, 'start')
        #name = current_thread().getName()
        self.func(*self.args)
        print(self.name, 'stop')

# 消费者
class Comsumer(Thread):

    def __init__(self, func, name=""):
        Thread.__init__(self)
        self.func = func
        self.name = name

    def run(self):
        print(self.name, 'start')
        #name = current_thread().getName()
        global queue
        # 消费完就结束
        while (not queue.empty()) or (len(dones) < len(questionIds)):
            try:
                obj = queue.get(timeout=10)
            except:
                # 10s获取不到说明没有消息产生 退出消费者
                break
            queue.task_done()
            self.func(obj['imgUrl'], obj['filePath'])
            print(f'{self.name} 下载完毕：{obj["title"]} - {obj["author"]} - {obj["imgUrl"]} - 队列中剩余{queue.qsize()}条未消费')
        print(self.name, 'stop')

# 装饰器
def timmer(func):
    print(f'{func.__name__} start......')
    def wrapper(*args):
        start_time = time.time()
        func(*args)
        stop_time = time.time()
        print(f'{func.__name__}运行时间是{stop_time - start_time}s')
    print(f'{func.__name__} end......')
    return wrapper

# 超级蜘蛛侠
@timmer
def superSpiderMan():
    # 创建爬虫实例
    spider = SpiderMan()

    # 生产者数组
    producers = []
    # 创建生产者
    for index, questionId in enumerate(questionIds):
        # args参数加上","才会当作一个列表/元组传递
        producer = Producer(spider.getAnswer, args=(questionId, ), name="producer" + str(index))
        producer.start()
        producers.append(producer)
    
    # 让生产者生产一会消息
    time.sleep(20)

    # 消费者数组
    consumers = []
    grouper = len(questionIds) * 3
    grouper = 15 if grouper >= 15 else grouper
    # 创建消费者
    for i in range(grouper):
        # 消费者
        consumer = Comsumer(spider.download_jpg, name="comsumer" + str(i))
        consumer.start()
        consumers.append(consumer)

    # 主线程等待子线程结束
    for producer in producers:
        producer.join()
    for consumer in consumers:
        consumer.join()


# 大自然的搬运工
@timmer
def mover(dictionary):
    f = local_path + dictionary
    print(f)
    # 创建新文件夹
    first_path, next_path, path = f.split("\\")
    new_path = os.path.join(first_path + os.path.sep, next_path)
    new_path = os.path.join(new_path, "all_" + path)
    # 判断文件夹是否存在
    if not os.path.exists(new_path):
        os.makedirs(new_path) 
    # 遍历当前文件夹
    for dir in os.listdir(f):
        print(dir)
        # 切换工作目录
        os.chdir(os.path.join(f, dir))
        # 获取当前目录路径
        work_path = os.getcwd()
        # 取当前工作目录下所有文件
        for file in os.listdir(work_path):
            # 取得文件路径
            file_path = os.path.join(work_path, file)
            # 需要复制的文件路径
            new_file = os.path.join(new_path, dir + "---" + file)
            print(f'开始复制：{new_file}')
            # 复制
            shutil.copy(file_path, new_file)

# 递归删除空文件夹
@timmer
def remover():
    dir_list = []
    for root, dirs, files in os.walk("D:\zhihu"):
        dir_list.append(root)
    #先生成个文件夹的列表，重点是下边
    for root in dir_list[::-1]:
        if not os.listdir(root):
            os.rmdir(root)

# 本地存储路径
local_path = 'D:\\zhihu\\'
# 创建一个队列
queue = queue.Queue(100000)
# 问题id, 注释掉的是已下载的
questionIds = [
        #'305888519',
        #'292901966',
        # '58498720',
        # '268395554',
        # '33797069',
        # '356413579',
        # '328457531',
        # '30061914',
        # '297715922',
        # '285321190',
        # '308457217',
        # '26297181',
        # '35139507',
        # '60627166',
        # '281794511'
        # '279938742',
        # '350859986',
        # '26037846',
        # '264285326',
        # '334483667',
        # '268863322',
        # '267453137',
        # '333026642',
        # '269910910',
        # '269764483',
        # '294981637',
        # '266808424',
        # '267707433',
        # '55105201',
        # '34243513',
        # '313825759',
        # '322577501',
        #  '352054645',
        #  '29815334',
        #  '319371540',
        #  '350710025',
        #  '316509144',
        #  '265911703',
        #  '295618890',
        #  '26652553',
        #  '297868711',
        #  '319709102',
        #  '44004717',
        #  '294151930',
        #  '303921863',
        #  '60199335',
        #  '298305248',
        #  '370052996',
        #  '332510604',
    ]
# 已下载问题的数组
dones = []

if __name__ == '__main__':
    # 超级蜘蛛侠出生了！
    superSpiderMan()
    
    # 删除空文件夹
    remover()

    # copy
    for dictionary in dones:
        mover(dictionary)

    # 任务结束退出主进程
    try:
        sys.exit('All job is done, Goodbye!')
    except Exception as e:
        print(f'the information of SystemExit:{e}')
        print("the program doesn't exit!")
    print('Now,the spider game is over!')





# -*- coding: utf-8 -*-

import itchat, time, re
from itchat.content import *

# 如果发送的是文字
@itchat.msg_register([TEXT])
def text_reply(msg):
	#match = re.search('', msg['Text'])
	#if match:
	itchat.send('[自动回复]', msg['FromUserName'])

# 如果发送的是图片，音频，视频和分享的东西
@itchat.msg_register([PICTURE,RECORDING,VIDEO,SHARING])
def other_reply(msg):
	itchat.send('[自动回复]', msg['FromUserName'])
 
itchat.auto_login(hotReload=True)
itchat.run()

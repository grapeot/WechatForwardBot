# -*- coding: utf-8 -*-
import itchat, time, re
from itchat.content import *
from utilities import *
from sys import argv, exit
from GlobalTextHook import GlobalTextHook
from HistoryRecorder import HistoryRecorder
from GroupTagCloud import GroupTagCloud
from GroupMessageForwarder import GroupMessageForwarder
from ProcessInterface import ProcessInterface
from ActivityInfo import ActivityInfo
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Some global switches for debugging use only
isDebug = not True

# Component initialization
itchat.auto_login(True)
plugins = [
    GlobalTextHook({ '^ding$': 'dong', '鸭哥': '嘎？' }),
    HistoryRecorder(),
    GroupTagCloud('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'),
    ActivityInfo('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'),
    GroupMessageForwarder([ '一群', '二群' ], [ '【科大校友AI&amp;Deep-Learning群】', '科大AI二群测试中' ], False),
    GroupMessageForwarder([ '二群', '三群' ], [ '科大AI二群测试中', '科大AI三群供测试' ])
]
for plugin in plugins:
    if not isinstance(plugin, ProcessInterface):
        logging.error('One of the plugins are not a subclass of ProcessInterface.')
        exit(-1)

# Core message loops
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def picture_reply(msg):
    if isDebug:
        logging.info(msg)
    for plugin in plugins:
        plugin.process(msg, PICTURE)

@itchat.msg_register([SHARING], isGroupChat=True)
def sharing_reply(msg):
    if isDebug:
        logging.info(msg)
    for plugin in plugins:
        plugin.process(msg, SHARING)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if isDebug:
        logging.info(msg)
    for plugin in plugins:
        plugin.process(msg, TEXT)

if __name__ == '__main__':
    itchat.run()

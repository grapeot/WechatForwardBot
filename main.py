# -*- coding: utf-8 -*-
import itchat, time, re
from itchat.content import *
from utilities import *
from sys import argv, exit
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Important parameters
chatroomDisplayNames = [ 'group1', 'group2' ]

# Some global switches for debugging use only
isBidirectional = True
isDebug = not True

# Initialize the itchat client and chatrooms
itchat.auto_login(True)
chatrooms = itchat.get_chatrooms()
chatroomNames = [ getNameForChatroomDisplayName(x) for x in chatroomDisplayNames ]
chatroomObjs = [ getChatroomByName(chatrooms, x) for x in chatroomNames ]
if len([ x for x in chatroomObjs if x is None ]) != 0:
    exit(-1)
chatroomIds = [ x['UserName'] for x in chatroomObjs ]
nickNameLookup = NickNameLookup(chatroomObjs)
logging.info('Fetched user ids for the chatrooms.')

def shallSend(msg):
    result = False
    for i in range(len(chatroomIds)):
        result = result or extractToUserName(msg) == chatroomIds[i] or extractFromUserName(msg) == chatroomIds[i]
        if result:
            return { 'shallSend': True, 'fromChatroom': i }
        if not isBidirectional:
            break
    return { 'shallSend': False }

# Core message loops
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def picture_reply(msg):
    if isDebug:
        logging.info(msg)
    shallSendObj = shallSend(msg)
    if not shallSendObj['shallSend']:
        return
    msg['Text'](msg['FileName'])
    type = {'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil')
    typeText = {'Picture': '图片', 'Video': '视频'}.get(msg['Type'], '文件')
    fromText = '[{0}]'.format(chatroomDisplayNames[shallSendObj['fromChatroom']])
    destinationChatroomId = chatroomIds[not shallSendObj['fromChatroom']]
    content = '{0} {1} 发送了{2}:'.format(fromText, nickNameLookup.lookupNickName(msg), typeText)
    itchat.send(content, destinationChatroomId)
    logging.info(content)
    itchat.send('@{0}@{1}'.format(type, msg['FileName']), destinationChatroomId)

@itchat.msg_register([SHARING], isGroupChat=True)
def sharing_reply(msg):
    if isDebug:
        logging.info(msg)
    shallSendObj = shallSend(msg)
    if not shallSendObj['shallSend']:
        return
    fromText = '[{0}]'.format(chatroomDisplayNames[shallSendObj['fromChatroom']])
    destinationChatroomId = chatroomIds[not shallSendObj['fromChatroom']]
    content = '{0} {1}分享了链接: {2} {3}'.format(fromText, nickNameLookup.lookupNickName(msg), msg['Text'], msg['Url'])
    logging.info(content)
    itchat.send(content, destinationChatroomId)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_reply(msg):
    if isDebug:
        logging.info(msg)
    shallSendObj = shallSend(msg)
    if not shallSendObj['shallSend']:
        return
    fromText = '[{0}]'.format(chatroomDisplayNames[shallSendObj['fromChatroom']])
    destinationChatroomId = chatroomIds[not shallSendObj['fromChatroom']]
    content = '{0} {1}: {2}'.format(fromText, msg['ActualNickName'], msg['Content'])
    logging.info(content)
    itchat.send(content, destinationChatroomId)

if __name__ == '__main__':
    itchat.run()

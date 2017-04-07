# -*- coding: utf-8 -*-
"""
Some utility functions
"""
from pymongo import MongoClient
import logging

# Some global configuration
dbName = 'WechatHistory'
collName = 'history'
gaCollName = 'GaNum'
client = MongoClient('localhost', 27017)

class NickNameLookup:
    def __init__(self, chatrooms):
        self.dict = {}
        for chatroom in chatrooms:
            for member in chatroom['MemberList']:
                self.dict[member['UserName']] = member['DisplayName'] if member['DisplayName'] != '' else member['NickName']

    def lookupNickName(self, msg):
        if 'ActualNickName' in msg and msg['ActualNickName'] != '':
            return msg['ActualNickName']
        username = msg['ActualUserName']
        if username in self.dict:
            return self.dict[username]
        else:
            return '未知昵称'

def extractFromUserName(msg):
    # It's messy that if the sender is yourself, the group name will appear in the ToUserName
    if 'ToUserName' in msg and msg['ToUserName'] != '':
        return msg['ToUserName']

def extractToUserName(msg):
    # For group chat FromUserName is the group Id
    if 'FromUserName' in msg and msg['FromUserName'] != '':
        return msg['FromUserName']
    elif 'User' in msg and msg['User']['UserName'] != '':
        return msg['User']['UserName']
    else:
        return '未知昵称'

def getChatroomByName(chatrooms, name):
    groups = [ x for x in chatrooms if x['NickName'] == name ]
    if len(groups) == 0:
        logging.error('Cannot find the chatroom named {0}.'.format(name))
        return None
    return groups[0]

def getNameForChatroomDisplayName(name):
    return name.replace('&', '&amp;')

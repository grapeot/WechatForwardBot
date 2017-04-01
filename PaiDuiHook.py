from itchat.content import *
from ProcessInterface import ProcessInterface
import itchat
import re
import logging

class PaiDuiHook(ProcessInterface):
    groupContentCacheMaxCapacity = 10

    def __init__(self, blacklist=[]):
        self.blacklist = blacklist
        self.groupLastMsgsDict = {}
        logging.info('PaiduiHook initialized.')

    def WhatToPaiDui(self, groupName):
        msgCount = {}
        msgs = self.groupLastMsgsDict[groupName]
        for msg in msgs:
            if msg['Content'] not in msgCount:
                msgCount[msg['Content']] = 0
            msgCount[msg['Content']] += 1
            if msg['FromSelf']:
                # if we replied this before, we will effectively remove it from the group content cache
                msgCount[msg['Content']] -= self.groupContentCacheMaxCapacity
        contentToPaiDui = [ x for x in msgCount if msgCount[x] > 1 ]
        if len(contentToPaiDui) > 1:
            logging.error('Something is wrong, len(contentToPaiDui) > 1.')
        if len(contentToPaiDui) == 0:
            return None
        else:
            return contentToPaiDui[0]

    def isFromSelf(self, msg):
        if re.search('^@@', msg['ToUserName']):
            return True
        else:
            return False

    def updateGroupContentCache(self, msg, groupName):
        if groupName not in self.groupLastMsgsDict:
            self.groupLastMsgsDict[groupName] = []
        if len(self.groupLastMsgsDict[groupName]) >= self.groupContentCacheMaxCapacity:
            self.groupLastMsgsDict[groupName].pop(0)
        self.groupLastMsgsDict[groupName].append({ 'Content': msg['Content'], 'FromSelf': 'FromSelf' in msg and msg['FromSelf'] })

    def process(self, msg, type):
        if type != TEXT:
            return
        groupName = msg['User']['NickName']
        if any([ re.search(x, groupName) is not None for x in self.blacklist ]):
            return
        if re.search('^/', msg['Content']):
            return
        if self.isFromSelf(msg):
            # Stop processing if the message is from myself
            return

        self.updateGroupContentCache(msg, groupName)
        contentToPaiDui = self.WhatToPaiDui(groupName)
        if contentToPaiDui is not None:
            # Pai dui!
            itchat.send(msg['Content'], msg['FromUserName'])
            logging.info('Pai Dui! {0}.'.format(msg['Content']))
            # Update data structure to avoid Pai dui for multiple times.
            self.updateGroupContentCache({ 'Content': msg['Content'], 'FromSelf': True }, groupName)

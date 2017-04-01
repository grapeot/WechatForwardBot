from itchat.content import *
from ProcessInterface import ProcessInterface
import itchat
import re
import logging

class PaiDuiHook(ProcessInterface):
    groupContentCacheMaxCapacity = 5
    maxSelfPaiDuiTTL = 15

    def __init__(self, blacklist=[]):
        self.blacklist = blacklist
        self.groupLastMsgsDict = {}
        # A dictionary controlling not pai dui for more than one time
        # Key: (groupName, content), Value: TTL (0 or non-exist means OK to paidui)
        self.selfPaiDuiTTL = {}   
        logging.info('PaiduiHook initialized.')

    def WhatToPaiDui(self, groupName):
        msgCount = {}
        msgs = self.groupLastMsgsDict[groupName]
        for msg in msgs:
            if msg['Content'] not in msgCount:
                msgCount[msg['Content']] = 0
            msgCount[msg['Content']] += 1
        contentToPaiDui = [ x for x in msgCount if msgCount[x] > 1 ]
        if len(contentToPaiDui) == 0:
            # No dui to pai
            return
        # it's possible that two duis are formed at the same time, but only one can pass the TTL check
        for content in contentToPaiDui:
            if (groupName, content) not in self.selfPaiDuiTTL or self.selfPaiDuiTTL == 0:
                self.selfPaiDuiTTL[(groupName, content)] = self.maxSelfPaiDuiTTL
                yield content  # We use yield here because we still need to conitnue managing the TTL
            else:
                self.selfPaiDuiTTL[(groupName, content)] -= 1

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
        self.groupLastMsgsDict[groupName].append({ 'Content': msg['Content'] })

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
        contentToPaiDui = list(self.WhatToPaiDui(groupName))
        if len(contentToPaiDui) > 1:
            logging.error('Multiple duis detected.')
        if len(contentToPaiDui) != 0:
            # Pai dui!
            itchat.send(msg['Content'], msg['FromUserName'])
            logging.info('Pai Dui! {0}.'.format(msg['Content']))
            # Update data structure to avoid Pai dui for multiple times.
            self.updateGroupContentCache({ 'Content': msg['Content'], 'FromSelf': True }, groupName)

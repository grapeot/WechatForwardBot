# -*- coding: utf-8 -*-
from utilities import *
from itchat.content import *
from collections import Counter
from pymongo import MongoClient, DESCENDING
from wordcloud import WordCloud
from ProcessInterface import ProcessInterface
import os
import itchat
import re
import random
import time
import logging
import jieba
import numpy as np
from PIL import Image

class GroupTagCloud(ProcessInterface):
    recordMaxNum = 500
    maxFrequency = 40
    imgDir = 'TagCloud'

    def __init__(self, fontPath, maskPath = None):
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        self.fontPath = fontPath
        if maskPath is None:
            self.wordCloud = WordCloud(font_path=self.fontPath, width=400, height=400, max_words=100)
        else:
            self.mask = np.array(Image.open(maskPath))
            self.wordCloud = WordCloud(font_path=self.fontPath, mask=self.mask, max_words=100)
        if not os.path.exists(self.imgDir):
            os.mkdir(self.imgDir)
        logging.info('GroupTagCloud connected to MongoDB.')

    def process(self, msg, type):
        shallRunObj = self.isRun(msg, type)
        if shallRunObj['shallRun']:
            logging.info('Generating tag cloud for {0}.'.format(shallRunObj['groupName']))
            fn = self.generateTagCloudForGroup(shallRunObj['groupName'], shallRunObj['userName'])
            destinationChatroomId = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg['ToUserName']
            logging.info('Sending tag cloud file {0} to {1}.'.format(fn, destinationChatroomId))
            itchat.send('@img@{0}'.format(fn), destinationChatroomId)

    # Generate a tag cloud image from the latest self.recordMaxNum images. Return the file name.
    def generateTagCloudForGroup(self, groupName, userName=None):
        records = None
        if userName is None:
            records = self.coll.find({ 'to': groupName }).sort([ ('timestamp', DESCENDING) ]).limit(self.recordMaxNum)
        else:
            records = self.coll.find({ 'from': userName, 'to': groupName }).sort([ ('timestamp', DESCENDING) ]).limit(self.recordMaxNum)
        texts = [ r['content'] for r in records ]
        frequencies = Counter([ w for text in texts for w in jieba.cut(text, cut_all=False) if len(w) > 1 ])
        frequencies = { k: min(self.maxFrequency, frequencies[k]) for k in frequencies }
        img = self.wordCloud.generate_from_frequencies(frequencies).to_image()
        fn = self.generateTmpFileName()
        img.save(fn)
        return fn

    def isRun(self, msg, type):
        if type != TEXT or 'Content' not in msg:
            return { 'shallRun': False }
        if re.search(r'^\s*/tagcloud$', msg['Content']):
            return { 'shallRun': True, 'userName': None, 'groupName': msg['User']['NickName'] }
        if re.search(r'^\s*/mytag$', msg['Content']):
            return { 'shallRun': True, 'userName': msg['ActualNickName'], 'groupName': msg['User']['NickName'] }
        return { 'shallRun': False }

    def generateTmpFileName(self):
        return '{0}/{1}-{2}.png'.format(self.imgDir, int(time.time() * 1000), random.randint(0, 10000))

if __name__ == '__main__':
    groupTagCloud = GroupTagCloud('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
    groupTagCloud.generateTagCloudForGroup('TestGroup')

# -*- coding: utf-8 -*-
from utilities import *
from itchat.content import *
from collections import Counter
from pymongo import MongoClient, DESCENDING
from wordcloud import WordCloud
from ProcessInterface import ProcessInterface
import itertools
import gensim
import os
import itchat
import re
import random
import time
import logging
import jieba

class GroupTagCloud(ProcessInterface):
    recordMaxNum = 500
    maxFrequency = 40
    imgDir = 'TagCloud'

    def __init__(self, fontPath):
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        self.fontPath = fontPath
        self.wordCloud = WordCloud(font_path=self.fontPath, width=400, height=400, max_words=100)
        if not os.path.exists(self.imgDir):
            os.mkdir(self.imgDir)
        logging.info('GroupTagCloud connected to MongoDB.')

    def process(self, msg, type):
        shallRunObj = self.isRun(msg, type)
        if shallRunObj['shallRun']:
            toLog = 'Generating tag cloud for {0}.'.format(shallRunObj['groupName'])
            if shallRunObj['userName']:
                toLog = '{0} Username {1}.'.format(toLog, shallRunObj['userName'])
            logging.info(toLog)
            fn = self.generateTagCloudForGroupV2(shallRunObj['groupName'], shallRunObj['userName'])
            destinationChatroomId = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg['ToUserName']
            logging.info('Sending tag cloud file {0} to {1}.'.format(fn, destinationChatroomId))
            itchat.send('@img@{0}'.format(fn), destinationChatroomId)

    # Generate a tag cloud image from the latest self.recordMaxNum records, based on TF-IDF. Return the file name.
    def generateTagCloudForGroupV2(self, groupName, userName=None):
        records = None
        if userName is None:
            records = self.coll.find({ 'to': groupName }).sort([ ('timestamp', DESCENDING) ]).limit(self.recordMaxNum)
            allRecords = self.coll.find({ 'to': { '$ne': groupName } }).sort([ ('timestamp', DESCENDING) ]).limit(self.recordMaxNum * 5)
            allRecordsGroup = sorted(allRecords, key=lambda x: x['to'])
        else:
            records = self.coll.find({ 'from': userName, 'to': groupName }).sort([ ('timestamp', DESCENDING) ]).limit(self.recordMaxNum)
            allRecords = self.coll.find({ 'from': { '$ne': userName }, 'to': groupName }).sort([ ('timestamp', DESCENDING) ]).limit(self.recordMaxNum * 5)
            allRecordsGroup = sorted(allRecords, key=lambda x: x['from'])
        docThisGroup = list(jieba.cut(' '.join([ r['content'] for r in records if re.match('<<<IMG', r['content']) is None])))  # remove the image records
        allRecordsGroup = itertools.groupby(allRecordsGroup, lambda x: x['to'])
        docsOtherGroups = [ list(jieba.cut(' '.join([x['content'] for x in list(g) if re.match('<<<IMG', x['content']) is None]))) for k, g in allRecordsGroup ]
        docs = [ docThisGroup ] + docsOtherGroups
        dictionary = gensim.corpora.Dictionary(docs)
        docs = [ dictionary.doc2bow(doc) for doc in docs ]
        id2token = { v: k for k, v in dictionary.token2id.items() }
        tfidf = gensim.models.tfidfmodel.TfidfModel(corpus=docs)
        tagCloudFrequencies = { id2token[x[0]]: x[1] for x in tfidf[docs[0]] }

        img = self.wordCloud.generate_from_frequencies(tagCloudFrequencies).to_image()
        fn = self.generateTmpFileName()
        img.save(fn)
        return fn

    # Generate a tag cloud image from the latest self.recordMaxNum messages. Return the file name.
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
    groupTagCloud.generateTagCloudForGroup('知乎万粉俱乐部', '鸭哥')
    groupTagCloud.generateTagCloudForGroupV2('知乎万粉俱乐部', '鸭哥')

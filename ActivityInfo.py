# -*- coding: utf-8 -*-
from utilities import *
from itchat.content import *
from ProcessInterface import ProcessInterface
from pymongo import MongoClient, DESCENDING
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pp
from matplotlib.font_manager import FontProperties
from matplotlib.dates import HourLocator, DateFormatter
import numpy as np
from time import time
from collections import Counter
from datetime import datetime
import itchat
import random
import re
import os
import logging

class ActivityInfo(ProcessInterface):
    timestampSubtract = 3600 * 24  # 1 day
    maxActivityInfoCount = 10
    imgDir = 'activityInfo'

    def __init__(self, fontPath):
        if not os.path.exists(self.imgDir):
            os.mkdir(self.imgDir)
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        self.prop = FontProperties(fname=fontPath)
        logging.info('ActivityInfo initialized.')

    def process(self, msg, type):
        if type != TEXT:
            return
        if msg['Content'] == '/activity':
            logging.info('Generating activity info for {0}.'.format(msg['User']['NickName']))
            fn = self.generateActivityInfoForGroup(msg['User']['NickName'])
            destinationChatroomId = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg['ToUserName']
            logging.info('Sending activity file {0} to {1}.'.format(fn, destinationChatroomId))
            itchat.send('@img@{0}'.format(fn), destinationChatroomId)

    def generateActivityInfoForGroup(self, groupName):
        timestampNow = int(time())
        timestampYesterday = timestampNow - self.timestampSubtract
        records = list(self.coll.find({ 'to': groupName, 'timestamp': { '$gt': timestampYesterday } }).sort([ ('timestamp', DESCENDING) ]))
        fn = self.generateTmpFileName()
        # Get histogram for activity
        hist, bins = np.histogram([ x['timestamp'] for x in records ], bins=24)
        center = (bins[:-1] + bins[1:]) / 2
        datex = [ datetime.fromtimestamp(x) for x in center ]
        pp.figure(figsize=(6,14))
        ax = pp.subplot(2, 1, 1)
        pp.plot_date(datex, hist, '.-')
        pp.gcf().autofmt_xdate()
        pp.xlabel(u'美国西部时间', fontproperties=self.prop)
        pp.ylabel(u'每小时消息数', fontproperties=self.prop)
        ax.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M'))
        # Get bar chart for active users
        pieDat = Counter([ x['from'] for x in records ])
        pieDatSorted = sorted([ (k, pieDat[k]) for k in pieDat ],key=lambda x: x[1], reverse=True)
        if len(pieDatSorted) > self.maxActivityInfoCount:
            pieDatSorted = pieDatSorted[:self.maxActivityInfoCount]
        ax = pp.subplot(2, 1, 2)
        width = 0.7
        x = np.arange(len(pieDatSorted)) + width
        xText = [ xx[0] for xx in pieDatSorted ]
        y = [ xx[1] for xx in pieDatSorted ]
        pp.bar(x, y, width)
        a = pp.gca()
        a.set_xticklabels(a.get_xticks(), { 'fontProperties': self.prop })
        pp.xticks(x, xText, rotation='vertical')
        pp.xlabel(u'用户', fontproperties=self.prop)
        pp.ylabel(u'24小时消息数', fontproperties=self.prop)
        ax.set_xlim([ 0, len(xText) + 1 - width ])
        pp.margins(0.2)
        pp.savefig(fn)
        return fn

    def generateTmpFileName(self):
        return '{0}/{1}-{2}.png'.format(self.imgDir, int(time() * 1000), random.randint(0, 10000))

if __name__ == '__main__':
    ai = ActivityInfo('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
    ai.generateActivityInfoForGroup('💦人美三观正之嘴炮无下限')

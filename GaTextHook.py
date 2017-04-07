# -*- coding: utf-8 -*-

from itchat.content import *
from ProcessInterface import ProcessInterface
from utilities import *
from time import time, sleep
from threading import Timer
from datetime import datetime
import itchat
import re
import logging
    
def clearGaNumDict():
    GaTextHook.gaNumDict = {}
    client[dbName][gaCollName].remove({}, {'multi': True})
    logging.info('GaNumDict cleared. GaNumDict = {0}.'.format(GaTextHook.gaNumDict))
    scheduleTimerToClearGaNumDict()

def scheduleTimerToClearGaNumDict():
    t = datetime.today()
    t2 = t.replace(day=t.day+1, hour=9, minute=0, second=0, microsecond=0) # 0:00 in China
    deltaT = t2 - t
    secs = deltaT.seconds + 1
    Timer(secs, clearGaNumDict).start()

# The logic is getting more complicated. We make it a seprate processor
class GaTextHook(ProcessInterface):
    gaNumDict = {}
    def __init__(self, blacklist=[]):
        self.blacklist = blacklist
        self.client = client
        self.gaColl = self.client[dbName][gaCollName]
        GaTextHook.gaNumDict = { x['GroupName']: x['CurrentGaNum'] for x in self.gaColl.find() }
        self.gaNumMax = 100
        self.triggerText = '鸭哥'
        self.gaText = '嘎？'
        self.forceTriggerText = '鸭哥嘎一个'
        self.forceTriggerNextTimestamp = {}
        self.forceTriggerInterval = 5 * 60 # 5 minutes
        self.forceTriggerGaText = '强力嘎！'
        scheduleTimerToClearGaNumDict()

        # Set up the clear timer
        logging.info('GaTextHook initialized.')

    def process(self, msg, type):
        if type != TEXT:
            return
        groupName = msg['User']['NickName']
        toSend = None
        if any([ re.search(x, groupName) is not None for x in self.blacklist ]):
            return
        if re.search(self.forceTriggerText, msg['Content']):
            currentTime = time()
            gaNextTime = self.forceTriggerNextTimestamp.get(groupName, 0)
            if currentTime < gaNextTime:
                logging.info("Don't force Ga because time {0} < NextTime {1} for group {2}.".format(currentTime, gaNextTime, groupName))
                return;
            self.forceTriggerNextTimestamp[groupName] = currentTime + self.forceTriggerInterval
            toSend = self.forceTriggerGaText
            logging.info('{0} => {1}'.format(msg['Content'], toSend))
            itchat.send(toSend, msg['FromUserName'])
            return
        if re.search(self.triggerText, msg['Content']):
            # Check the ga time
            if groupName not in GaTextHook.gaNumDict:
                GaTextHook.gaNumDict[groupName] = 0
            GaTextHook.gaNumDict[groupName] += 1
            self.gaColl.update({'GroupName': groupName}, {'$set': { 'CurrentGaNum': GaTextHook.gaNumDict[groupName] } }, upsert=True)
            if GaTextHook.gaNumDict[groupName] > self.gaNumMax:
                logging.info("Don't Ga because GaNum {0} exceeds max {1} for group {2}.".format(GaTextHook.gaNumDict[groupName], self.gaNumMax, groupName))
                return
            toSend = '{0} x{1}'.format(self.gaText, GaTextHook.gaNumDict[groupName])
            logging.info('{0} => {1}'.format(msg['Content'], toSend))
            itchat.send(toSend, msg['FromUserName'])

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    hook = GaTextHook()

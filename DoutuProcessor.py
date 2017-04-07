from time import time
from datetime import datetime
from ProcessInterface import ProcessInterface
from utilities import *
from itchat.content import *
from subprocess import call
from ImageSearcher import ImageSearcher
from threading import Thread
from time import time, sleep
import logging
import itchat
import re
import os

def DoutuEnd(destinationChatroomId):
    sleep(DoutuProcessor.doutuTimeInterval)
    itchat.send('时间到， 斗图结束。', destinationChatroomId)

class DoutuProcessor(ProcessInterface):
    doutuTimeInterval = 5 * 60   # seconds
    
    def __init__(self, doutuFeatureFn, whitelist=[]):
        self.imgFolder = 'DouTuRobot/dat/gifs/'
        self.doutuFolder = 'DoutuImages'
        self.whitelist = set(whitelist)
        self.activationTime = {}
        if not os.path.exists(self.doutuFolder):
            os.mkdir(self.doutuFolder)
        self.imageSearcher = ImageSearcher(doutuFeatureFn)
        logging.info('DoutuProcessor initialized.')

    def process(self, msg, type):
        # Mode management
        groupName = msg['User']['NickName']
        destinationChatroomId = msg['FromUserName'] if re.search('@@', msg['FromUserName']) else msg['ToUserName']
        if type == TEXT and msg['Content'] == '/doutu':
            # Control mode
            self.activationTime[groupName] = time() + self.doutuTimeInterval
            itchat.send('鸭哥进入斗图模式！ {0}分钟内群里所有照片和表情（除了商城表情），鸭哥都会回复斗图！'.format(int(self.doutuTimeInterval / 60)), destinationChatroomId)
            Thread(target=DoutuEnd, args=[destinationChatroomId]).start()
            return
        if type != PICTURE:
            return
        # If in whitelist. skip the mode check. Otherwise check the activation time.
        if groupName not in self.whitelist:
            if groupName not in self.activationTime or self.activationTime [groupName] <= time():
                return

        logging.info('[Doutu] Begin processing...')
        fn = msg['FileName']
        newfn = os.path.join(self.doutuFolder, fn)
        msg['Text'](fn)
        os.rename(fn, newfn)
        newfnjpg = newfn + '.jpg'
        call(['convert', '{0}[0]'.format(newfn), newfnjpg])
        if os.path.exists(newfnjpg):
            logging.info('[Doutu] imagemagick succeeded.')
        else:
            itchat.send('鸭哥没办法和腾讯表情商城的表情斗图。。', destinationChatroomId)
            logging.info('[Doutu] imagemagick failed.')
            return

        doutufn = self.imageSearcher.search(newfnjpg)
        doutufn = os.path.join(self.imgFolder, doutufn)
        itchat.send('@img@{0}'.format(doutufn), destinationChatroomId)
        logging.info('Doutu! {0} => {1}.'.format(newfn, doutufn))

if __name__ == '__main__':
    processor = DoutuProcessor('./DoutuFeatures.txt')

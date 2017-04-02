from time import time
from datetime import datetime
from pymongo import MongoClient
from ProcessInterface import ProcessInterface
from utilities import *
from itchat.content import *

class HistoryRecorder(ProcessInterface):
    def __init__(self):
        self.client = MongoClient()
        self.coll = self.client[dbName][collName]
        logging.info('HistoryRecorder connected to MongoDB.')

    # Record an itchat message to mongodb
    # Currently only support text messages in group chats
    def process(self, msg, type):
        if type != TEXT:
            return
        timestamp = time()
        rtime = datetime.utcfromtimestamp(timestamp)
        r = {
            'content': msg['Content'],
            'from': msg['ActualNickName'],
            'fromId': msg['ToUserName'],
            'to': msg['User']['NickName'] if 'User' in msg and 'UserName' in msg['User'] else 'N/A',
            'timestamp': timestamp,
            'time': rtime
            }
        self.coll.insert(r)

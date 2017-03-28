from itchat.content import *
from ProcessInterface import ProcessInterface
import itchat
import re
import logging

class GlobalTextHook(ProcessInterface):
    def __init__(self, subdict={}):
        self.dict = subdict
        logging.info('GlobalTextHook initialized.')

    def process(self, msg, type):
        if type != TEXT:
            return
        for k in self.dict:
            if re.search(k, msg['Content']):
                v = self.dict[k]
                logging.info('{0} => {1}'.format(msg['Content'], v))
                itchat.send(v, msg['FromUserName'])

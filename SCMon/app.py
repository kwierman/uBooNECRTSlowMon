import time
import logging
from SCMon.queries import MessageQuery
from SCMon.calculators import (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, DRVErrFlag_top, EVTRate_Sum, MaxBuff_OCC, MinBuff_OCC)
from SCMon import settings

class App():
    query_classes = (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, DRVErrFlag_top, EVTRate_Sum, MaxBuff_OCC, MinBuff_OCC)
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  settings.PID_PATH
        self.pidfile_timeout = 5
        self.__client__ = MessageQuery.default_client()
        self.__queries__ = [query_cls(__client__) for query_cls in self.query_classes]
            
    def run(self):

        while True:
            prev_time = int(time.time())
            updates= [query.update() for query in self.__queries__]
            current_time = int(time.time())
            time_to_sleep = current_time-prev_time-settings.POLL_RATE
            if time_to_sleep>0:
                time.sleep(time_to_sleep)
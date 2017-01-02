import time
import logging
from SCMon.calculators import (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, DRVErrFlag_top, EVTRate_Sum, MaxBuff_OCC, MinBuff_OCC)


class App():
    query_classes = (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, DRVErrFlag_top, EVTRate_Sum, MaxBuff_OCC, MinBuff_OCC)
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/scmon.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        while True:
            prev_time = time.now()
            updates= [query_cls(client).update() for query_cls in self.query_classes]
            current_time = time.now()
            time_to_sleep = current_time.seconds-prev_time.seconds-settings.POLL_RATE
            if time_to_sleep>0:
                time.sleep()
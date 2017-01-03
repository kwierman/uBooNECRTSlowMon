import time
import logging
from logging.handlers import RotatingFileHandler
from SCMon.queries import MessageQuery
from SCMon.calculations import query_classes
from SCMon import settings

class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  settings.PID_PATH
        self.pidfile_timeout = 5

        self.logger = logging.getLogger()
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = RotatingFileHandler(
              settings.LOG_PATH, maxBytes=2000000, backupCount=5)
        self.logger.setLevel(logging.DEBUG)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        self.__client__ = MessageQuery.default_client()
        self.__queries__ = [query_cls(client=self.__client__) for query_cls in query_classes]
            
    def run(self):

        while True:
            prev_time = int(time.time())
            updates= [query.update() for query in self.__queries__]
            current_time = int(time.time())
            time_to_sleep = current_time-prev_time-settings.POLL_RATE
            if time_to_sleep>0:
                time.sleep(time_to_sleep)
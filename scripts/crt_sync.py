import subprocess
import logging
from logging.handlers import RotatingFileHandler
import daemon
from daemon import runner
import time
import os

local_directory="/raid/tpc_timestamps"
remote_user="uboonepro"
remote_server="ubdaq-prod-evb"
remote_directory="/data/uboonedaq/rawdata"

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/home/kwierman/evb_sync.pid'
        self.pidfile_timeout = 5
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = RotatingFileHandler('/home/kwierman/evb_sync.log', maxBytes=1e8, backupCount=2)
        self.logger.setLevel(logging.INFO)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
    def sync_next(self):
        try:
            remote_string = "{}@{}:{}/*.json".format(remote_user,
                                          remote_server,
                                          remote_directory)
            success = subprocess.check_call(['rsync',remote_string,local_directory])
            self.logger.info("Update Success")
            return (success ==0)
        except:
            self.logger.info("Update did not succeed")
            return False
    def cleanup(self):
        current_files = os.listdir(local_directory)
        self.logger.info("Cleaning up files")
        for i in current_files:
            full_path = os.path.join(local_directory, i)
            age = os.stat(full_path).st_mtime
            one_week_ago = time.time()-float(60*60*24*7)
            if age<one_week_ago:
                self.logger.info("Cleaning Up: {}".format(full_path))
                os.remove(full_path)
    def run(self):
        while(1):
            sync = self.sync_next()
            self.cleanup()
            if sync:
                time.sleep(60)
            else:
                time.sleep(20)

if __name__ == "__main__":
    app = App()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[app.handler.stream]
    daemon_runner.do_action()

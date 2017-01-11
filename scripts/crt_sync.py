import subprocess
import logging
import daemon
import time
import os

local_directory="/data/tpc_timestamps"
remote_user="uboonepro"
remote_server="ubdaq-prod-evb"
remote_directory="/data/uboonedaq/rawdata"

class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  'evb_sync.pid'
        self.pidfile_timeout = 5
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = RotatingFileHandler('evb_sync.log', maxBytes=1e8, backupCount=2)
        self.logger.setLevel(logging.INFO)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
    def sync_next(self.):
        try:
            remote_string = "{}@{}:{}/*.json".format(remote_user,
                                          remote_server,
                                          remote_directory)
            success = subprocess.check_call(['rsync',,local_directory])
            return (success ==0)
        except:
            return False
    def cleanup(self):
        current_files = os.listdir(local_directory)
        for i in current_files:
            full_path = os.path.join(local_directory, i)
            age = os.stat(i).st_mtime
            one_week_ago = time.time()-float(60*60*24*7)
            if age<one_week_ago:
                os.remove(full_path)
    def run(self):
        while(1):
            sync = self.sync_next()
            #cleanup
            self.cleanup()
            if sync:
                time.sleep(60)


if __name__ == "__main__":
    app = App()
    daemon_runner = deamon.runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[app.handler.stream]
    daemon_runner.do_action()
    

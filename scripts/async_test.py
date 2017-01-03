from daemon import runner
from SCMon.app import App
from SCMon import settings
import logging

logging.basicConfig(filename=settings.LOG_PATH,level=logging.DEBUG)

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

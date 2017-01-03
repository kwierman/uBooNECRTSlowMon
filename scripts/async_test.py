from daemon import runner
from SCMon.app import App
from SCMon import settings
import logging

logging.basicConfig(filename=settings.LOG_PATH,level=logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(settings.LOG_PATH)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

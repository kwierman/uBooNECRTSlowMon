import logging
from daemon import runner
from SCMon.app import App

app = App()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/var/log/testdaemon/testdaemon.log")
handler.setFormatter(formatter)
logger.addHandler(handler)
daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

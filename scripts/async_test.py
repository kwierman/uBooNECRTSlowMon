from daemon import runner
from SCMon.app import App
from SCMon import settings

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

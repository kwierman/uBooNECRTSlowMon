import logging
from epics import PV
from SCMon import settings as sc_set

class BaseCalcMixin:
  logger = logging.getLogger(__name__)
  def update(self):
    value = self.get_value()
    return self.update2epics(value)

  def get_value(self):
    pass

  def update2epics(self, value):
    name = sc_set.BASE_PATH+"/"+self.path
    pv = PV(name)
    self.logger.info("Updating: " + name + " with value: {}".format(value))
    return pv.put(value, wait=False)
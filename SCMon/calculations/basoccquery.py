from SCMon import FEBStatsQuery
from SCMon.calculations.base import BaseCalcMixin
from SCMon import settings as sc_set

class BaseOccQuery(BaseCalcMixin, FEBStatsQuery):
  max_len = sc_set.OCC_UPDATE_RATE/sc_set.POLL_RATE
  def update(self):
    value = self.get_value()
    self.updates.append(value)
    if len(self.updates)>= self.max_len:
      value = sum(self.updates)/float(len(self.updates))
      self.updates=[]
      return self.update2epics(value)
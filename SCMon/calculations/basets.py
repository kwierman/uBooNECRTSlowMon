import logging
from SCMon import FEBStatsQuery
from SCMon.calculations.base import BaseCalcMixin
from SCMon import settings as sc_set

class BaseTSQuery(BaseCalcMixin, FEBStatsQuery):
  path=sc_set.TS1OK_PATH  
  logger = logging.getLogger(__name__)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS
  column_title='ts0ok'

  max_len = sc_set.OCC_UPDATE_RATE/sc_set.POLL_RATE
  def update(self):
    value = self.get_value()
    self.updates.append(value)
    if len(self.updates)>= self.max_len:
      value = sum(self.updates)/float(len(self.updates))
      self.updates=[]
      return self.update2epics(value)
      
  def get_value(self):
    self.limit=1000
    self.constraints = [sc_set.time_interval]
    try:
      df = self.construct_query()

      n_ok = 0
      for feb in self.febs:
        label = str(feb)
        if feb<10:
          label = "0{}".format(feb)
        ok=0.
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          index = 0 # len(feb_rows)-1
          ok = float(feb_rows[self.column_title][index])
        except:
          self.logger.warning("Could not find {} for: ".format(self.column_title)+label)
        n_ok+=float(ok)
      return n_ok/len(self.febs)
    except Exception as e:
      self.logger.error(e)
      return 0

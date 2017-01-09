import logging
from SCMon import FEBStatsQuery
from SCMon.calculations.base import BaseCalcMixin
from SCMon import settings as sc_set

class TS1OKQuery(BaseCalcMixin, FEBStatsQuery):
  path=sc_set.TS1OK_PATH  
  logger = logging.getLogger(__name__)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS

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
          index = len(feb_rows)-1
          ok = float(feb_rows['ts1ok'][index])
        except:
          self.logger.warning("Could not find ts0ok for: "+label)
        n_ok+=float(ok)
      return n_ok/len(self.febs)
    except Exception as e:
      self.logger.error(e)
      return 0
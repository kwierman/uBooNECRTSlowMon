from SCMon import FEBStatsQuery
from SCMon.calculations.base import BaseCalcMixin
import logging
from SCMon import settings as sc_set


class EVTRate_Sum(BaseCalcMixin, FEBStatsQuery):
  """
    Calculates the sum of event rates in the CRT and reports
    the sum to EPICS
  """
  path=sc_set.EVTRate_Sum_Path
  logger = logging.getLogger(__name__)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS

  def get_value(self):
    self.limit=1000
    self.constraints = [sc_set.time_interval]
    try:
      df = self.construct_query()

      ratesum=0.
      for feb in self.febs:
        label = str(feb)
        if feb<10:
          label = "0{}".format(feb)
        rate=0.
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          index = 0 # len(feb_rows)-1
          rate = float(feb_rows['evrate'][index])
        except:
          self.logger.warning("Could not find rate for: "+label)
        ratesum+=float(rate)
      return ratesum
    except Exception as e:
      self.logger.error(e)
      return 0

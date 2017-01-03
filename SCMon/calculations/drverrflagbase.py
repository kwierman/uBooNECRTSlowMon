from SCMon import FEBStatsQuery
from SCMon.calculations.base import BaseCalcMixin
import logging

class DRVErrFlag_Base(BaseCalcMixin, FEBStatsQuery):
  logger = logging.getLogger(__name__)
  febs = []

  def get_value(self):
    self.limit=1000
    self.constraints = ['time > now() - 1d']
    try:
      df = self.construct_query()

      for feb in self.febs:
        self.logger.debug("Working on FEB: "+str(feb))
        label=str(feb)
        if feb<10:
          label = "0{}".format(feb)
        feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
        index = len(feb_rows)-1
        lostcpu = feb_rows['lostcpu'][index]
        lostfpga = feb_rows['lostfpga'][index]
        ts0ok= feb_rows['ts0ok'][index]
        ts1ok = feb_rows['ts1ok'][index]
        if lostcpu==0 and lostfpga==0 and ts0ok==None and ts1ok==None:
          return 1
    except Exception as e:
      self.logger.error(e)
      return -1
    return 0
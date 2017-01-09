from SCMon import FEBStatsQuery
from SCMon.calculations.base import BaseCalcMixin
import logging
from SCMon import settings

class DRVErrFlag_Base(BaseCalcMixin, FEBStatsQuery):
  """
    Base class for driver error flag calculations.
    Overwrite `febs`  in derived classes to utilize.
  """
  logger = logging.getLogger(__name__)
  febs = []

  def get_value(self):
    """
      Gets the corresponding error flags from influx
      and if there are any bad values, updates the flag.

      :returns: 0 if good. 1 if bad, -1 if communication or 
      code errors.
    """
    self.limit=1000
    self.constraints = [settings.time_interval]
    try:
      df = self.construct_query()

      for feb in self.febs:
        self.logger.debug("Working on FEB: "+str(feb))
        label=str(feb)
        if feb<10:
          label = "0{}".format(feb)
        feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
        index = len(feb_rows)-1
        lostcpu = int(feb_rows['lostcpu'][index])
        lostfpga = int(feb_rows['lostfpga'][index])
        self.logger.info("Flags for feb: {}, {}, {}".format(feb, lostcpu, lostfpga))
        if lostcpu == 0 and lostfpga == 0:
          return 1.0
    except Exception as e:
      self.logger.error(e)
      return -1
    return 0.0
from SCMon.calculations.baseoccquery import BaseOccQuery
from SCMon import settings as sc_set
import logging

class MinBuff_OCC(BaseOccQuery):
  """
    Calculates out of all of the FEBs, what the
    minimum buffer occupancy is.
  """
  path=sc_set.MinBuff_OCC_Path
  logger = logging.getLogger(__name__)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS
  updates=[]
  
  def get_value(self):
    self.limit=1000
    min_rate = 1.e6
    self.constraints = [sc_set.time_interval]

    try:
      df = self.construct_query()
      ratesum=0
      for feb in self.febs:
        label=str(feb)
        if feb<10:
          label = "0{}".format(feb)
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          index = 0 # len(feb_rows)-1
          rate = float(feb_rows['evtsperpoll'][index])
          if rate < min_rate:
            min_rate = rate
        except:
          self.logger.warning("Could not find data for feb: "+label)
      return min_rate
    except Exception as e:
      self.logger.error(e)
      return -1

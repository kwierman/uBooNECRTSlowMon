import logging
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)

from epics import PV

PV_NAMING_SCHEME="{detector}_{subsys}_{rack}_{unit}/{var}"

def create_context():
    return {
        'detector':"uB",
        'subsys': 'DAQStatus',
        'rack': "CRTDAQX",
        'unit': 'evb',
        'var':''
    }

class BaseCalcMixin:
  def update(self):
    value = self.get_value()
    return self.update2epics(value)

  def get_value(self):
    pass

  def update2epics(self, value):
    context = create_context()
    context.var = self.path
    name = PV_NAMING_SCHEME.format(**context)
    pv = PV(name)
    return pv.put(value, wait=False)


class DRVErrFlag_Base(BaseCalcMixin, FEBStatsQuery):
  logger = logging.getLogger("DRVErrFlag")
  low=0
  high=9

  def get_value(self):
    self.limit=1
    for feb in range(self.low,self.high):
      if feb<10:
        feb = "0{}".format(feb)
      self.constraints = ['time > now() - 1d','host = "feb{}"'.format(feb)]
      try:
        df = self.construct_query()
        lostcpu = df['lost_cpu'][0]
        lostfpga = df['lost_fpga'][0]
        ts0ok= df['ts0ok'][0]
        ts1ok = df['ts1ok'][0]
        if lostcpu==0 and lostfpga==0 and ts0ok==None and ts1ok==None:
          return 1
      except:
        self.logger.warning("Could not construct Query for feb:"+str(feb))

    return 0

class DRVErrFlag_FTSide(DRVErrFlag_Base):
  path="drverrflag_FTSide"
  logger = logging.getLogger(path)
  low=9
  high=22

class DRVErrFlag_bottom(DRVErrFlag_Base):
  path="drverrflag_bottom"  
  logger = logging.getLogger(path)
  low=0
  high=9

class DRVErrFlag_pipeside(DRVErrFlag_Base):
  path="drverrflag_pipeside"
  logger = logging.getLogger(path)
  low =22
  high=49

class DRVErrFlag_top(DRVErrFlag_Base):
  path="drverrflag_top"
  logger = logging.getLogger(path)
  low=49
  high=77

class EVTRate_Sum(BaseCalcMixin, FEBStatsQuery):
  path="EVTRate_Sum"
  logger = logging.getLogger(path)
  low=0
  high=77

  def get_value(self):
    self.limit=1
    ratesum=0
    for feb in range(self.low,self.high):
      self.constraints = ['time > now() - 1d','host = "feb{}"'.format(feb)]
      df = self.construct_query()
      rate = df['evrate'][0]
      ratesum+=rate
    return ratesum


class MaxBuff_OCC(BaseCalcMixin, FEBStatsQuery):
  path="macbuff_occ"
  logger = logging.getLogger(path)
  low=0
  high=77

  def get_value(self):
    self.limit=1
    max_rate = -1.e6
    max_feb=0

    for feb in range(self.low,self.high):
      if feb<10:
        feb = "0{}".format(feb)
      self.constraints = ['time > now() - 1d','host = "feb{}"'.format(feb)]
      df = self.construct_query()
      rate = df['evrate'][0]
      if rate>max_rate:
        max_feb = feb
    return max_feb


class MinBuff_OCC(BaseCalcMixin, FEBStatsQuery):
  path="minbuff_occ"
  logger = logging.getLogger(path)
  low=0
  high=77

  def get_value(self):
    self.limit=1
    min_rate = 1.e6
    min_feb=0

    for feb in range(self.low,self.high):
      self.constraints = ['time > now() - 1d','host = feb{}'.format(feb)]
      df = self.construct_query()
      rate = df['evrate'][0]
      if rate<min_rate:
        min_feb = feb
    return min_feb



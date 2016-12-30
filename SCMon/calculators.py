import logging
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)
from SCMon import settings as sc_set

from epics import PV


def create_context():
    return {
        'detector':"uB",
        'subsys': 'DAQStatus',
        'rack': "CRTDAQX",
        'unit': 'evb',
        'var':''
    }


class BaseCalcMixin:
  logger = logging.getLogger("BaseCalculation")
  def update(self):
    value = self.get_value()
    return self.update2epics(value)

  def get_value(self):
    pass

  def update2epics(self, value):
    context = create_context()
    context['var'] = self.path
    name = sc_set.PV_NAMING_SCHEME.format(**context)
    pv = PV(name)
    self.logger.info("Updating: "+name + " with value: {}".format(value))
    return pv.put(value, wait=False)


class DRVErrFlag_Base(BaseCalcMixin, FEBStatsQuery):
  logger = logging.getLogger("DRVErrFlag")
  febs = sc_set.FT_FEBS

  def get_value(self):
    self.limit=100000
    self.constraints = ['time > now() - 1d']#,'host = "feb{}"'.format(feb)]
    try:
      df = self.construct_query()

      for feb in self.febs:
        self.logger.debug("Working on FEB: "+str(feb))
        label=str(feb)
        if feb<10:
          label = "0{}".format(feb)
        feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
        lostcpu = feb_rows['lostcpu'][0]
        lostfpga = feb_rows['lostfpga'][0]
        ts0ok= feb_rows['ts0ok'][0]
        ts1ok = feb_rows['ts1ok'][0]
        if lostcpu==0 and lostfpga==0 and ts0ok==None and ts1ok==None:
          return 1
    except Exception as e:
      self.logger.warning("Could not locate entries for feb:"+str(feb))
      self.logger.error(e)
      return -1
    return 0

class DRVErrFlag_FTSide(DRVErrFlag_Base):
  path="drverrflag_FTSide"
  logger = logging.getLogger(path)
  febs = sc_set.FT_FEBS

class DRVErrFlag_bottom(DRVErrFlag_Base):
  path="drverrflag_bottom"  
  logger = logging.getLogger(path)
  febs = sc_set.BOTTOM_FEBS

class DRVErrFlag_pipeside(DRVErrFlag_Base):
  path="drverrflag_pipeside"
  logger = logging.getLogger(path)
  febs = sc_set.PIPE_FEBS

class DRVErrFlag_top(DRVErrFlag_Base):
  path="drverrflag_top"
  logger = logging.getLogger(path)
  febs = sc_set.TOP_FEBS

class EVTRate_Sum(BaseCalcMixin, FEBStatsQuery):
  path="evtrate_sum"
  logger = logging.getLogger(path)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS

  def get_value(self):
    self.limit=100000
    self.constraints = ['time > now() - 1d']
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
          rate = float(feb_rows['evrate'][0])
        except:
          self.logger.warning("Could not find rate for: "+label)
        ratesum+=float(rate)
      return ratesum
    except Exception as e:
      self.logger.error(e)
      return 0


class MaxBuff_OCC(BaseCalcMixin, FEBStatsQuery):
  path="maxbuff_occ"
  logger = logging.getLogger(path)
  low=0
  high=77

  def get_value(self):
    self.limit=100000
    max_rate = -1.e6
    max_feb=0
    try:
      df = self.construct_query()
      ratesum=0
      for feb in range(self.low,self.high):
        label = str(feb)
        if feb<10:
          label = "0{}".format(feb)
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          rate = float(feb_rows['evrate'][0])
          if rate>max_rate:
            max_feb = feb
        except:
          self.logger.warning("Could not find data for feb: "+label)
      return max_feb
    except Exception as e:
      self.logger.error(e)
      return -1


class MinBuff_OCC(BaseCalcMixin, FEBStatsQuery):
  path="minbuff_occ"
  logger = logging.getLogger(path)
  low=0
  high=77

  def get_value(self):
    self.limit=1000000
    min_rate = 1.e6
    min_feb=0

    try:
      df = self.construct_query()
      ratesum=0
      for feb in range(self.low,self.high):
        label=str(feb)
        if feb<10:
          label = "0{}".format(feb)
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          rate = float(feb_rows['evrate'][0])
          if rate<min_rate:
            min_feb = feb
        except:
          self.logger.warning("Could not find data for feb: "+label)
      return min_feb
    except Exception as e:
      self.logger.error(e)
      return -1


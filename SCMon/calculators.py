import logging
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)
from SCMon import settings as sc_set

from epics import PV


class BaseCalcMixin:
  logger = logging.getLogger("BaseCalculation")
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
  path=sc_set.DRVErrFlag_FTSide_Path
  logger = logging.getLogger(path)
  febs = sc_set.FT_FEBS


class DRVErrFlag_bottom(DRVErrFlag_Base):
  path=sc_set.DRVErrFlag_bottom_Path
  logger = logging.getLogger(path)
  febs = sc_set.BOTTOM_FEBS


class DRVErrFlag_pipeside(DRVErrFlag_Base):
  path=sc_set.DRVErrFlag_pipeside_Path
  logger = logging.getLogger(path)
  febs = sc_set.PIPE_FEBS


class DRVErrFlag_top(DRVErrFlag_Base):
  path=sc_set.DRVErrFlag_top_Path
  logger = logging.getLogger(path)
  febs = sc_set.TOP_FEBS


class EVTRate_Sum(BaseCalcMixin, FEBStatsQuery):
  path=sc_set.EVTRate_Sum_Path
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
  path=sc_set.MaxBuff_OCC_Path
  logger = logging.getLogger(path)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS

  def get_value(self):
    self.limit=100000
    max_rate = -1.e6

    try:
      df = self.construct_query()
      ratesum=0
      for feb in self.febs:
        label = str(feb)
        if feb<10:
          label = "0{}".format(feb)
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          rate = float(feb_rows['evtsperpoll'][len(feb_rows['evtsperpoll'])-1])
          logging.debug("Rate found for Feb: {} : {}".format(label, rate))
          if rate>max_rate:
            max_rate = rate
        except:
          self.logger.warning("Could not find data for feb: "+label)
      return max_rate
    except Exception as e:
      self.logger.error(e)
      return -1


class MinBuff_OCC(BaseCalcMixin, FEBStatsQuery):
  path=sc_set.MinBuff_OCC_Path
  logger = logging.getLogger(path)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS

  def get_value(self):
    self.limit=1000000
    min_rate = 1.e6

    try:
      df = self.construct_query()
      ratesum=0
      for feb in self.febs:
        label=str(feb)
        if feb<10:
          label = "0{}".format(feb)
        try:
          feb_rows = df.loc[df['host'] == "\"feb{}\"".format(label)]
          rate = float(feb_rows['evtsperpoll'][0])
          if rate < min_rate:
            min_rate = rate
        except:
          self.logger.warning("Could not find data for feb: "+label)
      return min_rate
    except Exception as e:
      self.logger.error(e)
      return -1


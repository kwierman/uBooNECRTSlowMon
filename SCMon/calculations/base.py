import logging
from epics import PV
from SCMon import settings as sc_set

class BaseCalcMixin:
  """
    Defines the basic framework for a calculation
    style queries
  """
  logger = logging.getLogger(__name__)
  def update(self):
    """
      The main handling method for querying influxDB
      then updating EPICS
    """
    value = self.get_value()
    return self.update2epics(value)

  def get_value(self):
    """
      Dummy method. Overwrite this to instantiate
      influx interface
    """
    pass

  def update2epics(self, value):
    """
      Default update method for EPICS.
      :param value: The value to update corresponding to
      the column for this query type 
      :type value: object. Must have __str__ defined.
    """
    name = sc_set.BASE_PATH+"/"+self.path
    pv = PV(name)
    self.logger.info("Updating: " + name +
                     " with value: {}".format(value))
    return pv.put(value, wait=False)
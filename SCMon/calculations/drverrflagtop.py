import logging
from SCMon.calculations.drverrflagbase import DRVErrFlag_Base
from SCMon import settings as sc_set

class DRVErrFlag_Top(DRVErrFlag_Base):
  """
    Connection class for top side panel 
    CRT DRV error flag updates
  """
  path=sc_set.DRVErrFlag_top_Path
  logger = logging.getLogger(__name__)
  febs =  sc_set.TOP_FEBS

  def get_value(self):
    """
      This is a fix in place to ensure that
      this class is not used until the TOP 
      panel is installed.
    """
    return 0.0
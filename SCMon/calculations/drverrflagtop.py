import logging
from SCMon.calculations.drverrflagbase import DRVErrFlag_Base
from SCMon import settings as sc_set

class DRVErrFlag_Top(DRVErrFlag_Base):
  path=sc_set.DRVErrFlag_top_Path
  logger = logging.getLogger(__name__)
  febs = sc_set.TOP_FEBS

  def get_value(self):
    return 0
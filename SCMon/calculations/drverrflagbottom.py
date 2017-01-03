import logging
from SCMon.calculations.drverrflagbase import DRVErrFlag_Base
from SCMon import settings as sc_set

class DRVErrFlag_bottom(DRVErrFlag_Base):
  path=sc_set.DRVErrFlag_bottom_Path
  logger = logging.getLogger(__name__)
  febs = sc_set.BOTTOM_FEBS
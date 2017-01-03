import logging
from SCMon.calculations.drverrflagbase import DRVErrFlag_Base
from SCMon import settings as sc_set

class DRVErrFlag_FTSide(DRVErrFlag_Base):
  path = sc_set.DRVErrFlag_FTSide_Path
  logger = logging.getLogger(__name__)
  febs = sc_set.FT_FEBS

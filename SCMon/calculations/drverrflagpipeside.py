import logging
from SCMon.calculations.drverrflagbase import DRVErrFlag_Base
from SCMon import settings as sc_set

class DRVErrFlag_PipeSide(DRVErrFlag_Base):
  """
    Connection class for pipe side panel 
    CRT DRV error flag updates
  """
  path=sc_set.DRVErrFlag_pipeside_Path
  logger = logging.getLogger(__name__)
  febs = sc_set.PIPE_FEBS
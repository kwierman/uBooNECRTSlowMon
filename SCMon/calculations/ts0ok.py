import logging
from basets import BaseTSQuery

class TS0OKQuery(BaseTSQuery):
  path=sc_set.TS0OK_PATH
  logger = logging.getLogger(__name__)
  febs = sc_set.FT_FEBS+sc_set.BOTTOM_FEBS+sc_set.PIPE_FEBS+sc_set.TOP_FEBS
import logging
from basets import BaseTSQuery

class TS1OKQuery(BaseTSQuery):
  path=sc_set.TS1OK_PATH  
  logger = logging.getLogger(__name__)

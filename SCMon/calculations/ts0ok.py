import logging
from basets import BaseTSQuery

class TS0OKQuery(BaseTSQuery):
  path=sc_set.TS0OK_PATH
  logger = logging.getLogger(__name__)
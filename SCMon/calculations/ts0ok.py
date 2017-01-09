import logging
from basets import BaseTSQuery
from SCMon import settings as sc_set

class TS0OKQuery(BaseTSQuery):
  path=sc_set.TS0OK_PATH
  logger = logging.getLogger(__name__)
  updates=[]
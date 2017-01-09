import logging
from basets import BaseTSQuery
from SCMon import settings as sc_set

class TS1OKQuery(BaseTSQuery):
  path=sc_set.TS1OK_PATH  
  logger = logging.getLogger(__name__)
  updates=[]
  column_title='ts1ok'

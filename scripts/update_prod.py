"""
  Runs in the on-top update process.
"""
import logging
from SCMon.calculators import (DRVErrFlag_FTSide, DRVErrFlag_bottom, 
                                DRVErrFlag_pipeside, DRVErrFlag_top, 
                                EVTRate_Sum, MaxBuff_OCC, MinBuff_OCC)
query_classes = (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, 
                 DRVErrFlag_top, EVTRate_Sum, MaxBuff_OCC, MinBuff_OCC)

from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)
from time import sleep


def main(polltime=5):
  client = MessageQuery.default_client()
  global query_classes
  queries = [query_cls(client) for query_cls in query_classes]


  while( 1 ):
    try:
      updates= [query.update() for query in queries]
      sleep(polltime)
    except Exception as e:
      logging.error("Update Failed: {}".format(e))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

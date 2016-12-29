import logging
from SCMon.calculators import (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, DRVErrFlag_top, EVTRate_Sum)
query_classes = (DRVErrFlag_FTSide, DRVErrFlag_bottom, DRVErrFlag_pipeside, DRVErrFlag_top, EVTRate_Sum)


def main(polltime=1):
  client = MessageQuery.default_client()
  global query_classes

  while( 1 ):
    try:
      updates= [query_cls(client).update() for query_cls in query_classes]
    except Exception as e:
      logging.error("Update Failed: {}".format(e))
    sleep(polltime)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

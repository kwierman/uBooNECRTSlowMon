from epics import PV
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)
import settings
import logging
import daemon
import os

query_classes = (MessageQuery, FEBStatsQuery, DRVStatsQuery, EventsQuery)

os.environ["PYEPICS_LIBCA"] = settings.PYEPICS_LIBCA
os.environ["EPICS_BASE"] = settings.EPICS_BASE
os.environ["EPICS_HOST_ARCH"] = settings.EPICS_HOST_ARCH
os.environ["PATH"]=os.environ["PATH"]+":"+settings.EPICS_BASE+"/bin/"+settings.EPICS_HOST_ARCH+"/"


def create_context():
    return {
        'detector':"uB",
        'subsys': 'DAQStatus',
        'rack': "CRTDAQX",
        'unit': 'evb',
        'var':''
    }

def main():
  client = MessageQuery.default_client()
  global query_classes

  while( 1 ):
    for query_cls in query_classes:
        query = query_cls(client, columns='*',
                          constraints=settings.time_interval,
                          limit=settings.limit_queries)
        dataframe = query.construct_query()
        for column in dataframe:
            context = create_context()
            context['var']="{}_{}".format(query.table, column)
            pv = PV(settings.PV_NAMING_SCHEME.format(**context))
            data_type =dataframe[column].dtype
            time_set = dataframe[column].axes[0]
            for row, value in enumerate(dataframe[column]):
              time = time_set[row]
              print time, value
              if not value is pv.get():
                print value, pv.get()

    break

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()


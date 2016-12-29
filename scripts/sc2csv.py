#!python
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)

from optparse import OptionParser

def main(days, limit):
  client = MessageQuery.default_client()

  messages = MessageQuery(client, columns='*', constraints='time > now() - 1d', limit=100)
  mq =  messages.constuct_query()
  mq.to_csv("messages.csv")

  feb_stats = FEBStatsQuery(client, columns='*', constraints='time > now() - 1d', limit=100)
  fq =  feb_stats.constuct_query()
  mq.to_csv("feb_stats.csv")

  columns = [u'daqon', u'datime', u'host', u'msperpoll', u'nclients', u'status']
  drv_stats = DRVStatsQuery(client, columns=columns, constraints='time > now() - 1d', limit=100)
  dq =  drv_stats.constuct_query()
  dq.to_csv("dev_stats.csv")

  columns = [u'text', u'title']
  events = EventsQuery(client, columns='*', constraints='time > now() - 1d', limit=100)
  eq = events.constuct_query()
  eq.to_csv("events.csv")

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option("-d", "--days", dest="days", type=int,
                    help="Number of days to query", default=1)
  parser.add_option("-l", "--limit", dest="limit", type=int,
                    help="Maximum number of entries per column to query", default=1000)

  (options, args) = parser.parse_args()
  main(options.days, options.limit)
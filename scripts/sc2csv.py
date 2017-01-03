"""
  Dumps out the last `d` days up to `l` entries of influx entries
"""
#!python
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)

from optparse import OptionParser
import logging

def main(days, limit):
  client = MessageQuery.default_client()

  messages = MessageQuery(client, columns='*', 
                          constraints=['time > now() - {}d'.format(days)], 
                          limit=limit)
  mq =  messages.construct_query()
  mq.to_csv("messages.csv")

  feb_stats = FEBStatsQuery(client, columns='*', 
                            constraints=['time > now() - {}d'.format(days)], 
                            limit=limit)
  fq =  feb_stats.construct_query()
  fq.to_csv("feb_stats.csv")

  columns = [u'daqon', u'datime', u'host', u'msperpoll', u'nclients', u'status']
  drv_stats = DRVStatsQuery(client, columns=columns, 
                            constraints=['time > now() - {}d'.format(days)], 
                            limit=limit)
  dq =  drv_stats.construct_query()
  dq.to_csv("drv_stats.csv")

  columns = [u'text', u'title']
  events = EventsQuery(client, columns='*', 
                       constraints=['time > now() - {}d'.format(days)], 
                       limit=limit)
  eq = events.construct_query()
  eq.to_csv("events.csv")

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  parser = OptionParser()
  parser.add_option("-d", "--days", dest="days", type=int,
                    help="Number of days to query", default=1)
  parser.add_option("-l", "--limit", dest="limit", type=int,
                    help="Maximum number of entries per column to query", 
                    default=1000)

  (options, args) = parser.parse_args()
  main(options.days, options.limit)
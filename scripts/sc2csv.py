#!python
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)

client = MessageQuery._client

messages = MessageQuery(client, columns='*', constraints='time > now() - 1d', limit=100)
mq =  messages.constuct_query()
print type(mq)


"""
feb_stats = FEBStatsQuery(client, columns='*', constraints='time > now() - 1d', limit=100)
print feb_stats.constuct_query()

columns = [u'biason', u'configd', u'connectd', u'error', u'evrate', u'evtsperpoll', u'host', u'lostcpu', u'lostfpga', u'ts0ok', u'ts1ok']
feb_stats = FEBStatsQuery(client, columns=columns, constraints='time > now() - 1d', limit=100)
print feb_stats.constuct_query()

columns = [u'daqon', u'datime', u'host', u'msperpoll', u'nclients', u'status']
drv_stats = DRVStatsQuery(client, columns=columns, constraints='time > now() - 1d', limit=100)
print drv_stats.constuct_query()

columns = [u'text', u'title']
events = EventsQuery(client, columns='*', constraints='time > now() - 1d', limit=100)
print events.constuct_query()
"""

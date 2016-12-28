#!python
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)


client = MessageQuery._client


messages = MessageQuery(client, column='*', constraints='time > now() - 1d', limit=1000)
print messages.constuct_query()

messages = MessageQuery(client, column='text', constraints='time > now() - 1d', limit=1000)
print messages.constuct_query()

messages = MessageQuery(client, column='title', constraints='time > now() - 1d', limit=1000)
print messages.constuct_query()


feb_stats = FEBStatsQuery(client, column='*', constraints='time > now() - 1d', limit=1000)
print feb_stats.constuct_query()
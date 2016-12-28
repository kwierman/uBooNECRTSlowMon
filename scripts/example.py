#!python
from SCMon import (MessageQuery,
                   FEBStatsQuery,
                   DRVStatsQuery,
                   EventsQuery)


client = MessageQuery._client


messages = MessageQuery(client, column='*', constraints='time > now() - 1d', limit=1000)
print messages.list_series()
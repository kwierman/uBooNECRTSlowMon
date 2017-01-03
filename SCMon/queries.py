"""
  Table definitions for each of the tables in the CRT interface
"""

from SCMon.base import BaseQuery

class MessageQuery(BaseQuery):
  table = "messages"
class FEBStatsQuery(BaseQuery):
  table = "febstats"
class DRVStatsQuery(BaseQuery):
  table = "drvstats"
class EventsQuery(BaseQuery):
  table = "events"
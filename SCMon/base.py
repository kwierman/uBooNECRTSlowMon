"""
  Constructs the basic queries for the CRT system.
"""
from influxdb import InfluxDBClient, DataFrameClient
import logging

class BaseQuery:
  logger = logging.getLogger("BaseQuery")
  _client = DataFrameClient('localhost', 8086, 'root', 'root', 'crt')
  table = "messages"

  @classmethod
  def default_client(cls):
    return cls._client

  def __init__(self, client=None, columns=None, constraints=None, limit=None):
    if client is not None:
      self.client = client
    else:
      self.client = _client
    self.columns = columns
    self.constraints=None
    self.limit = limit

  def list_series(self):
    return self.client.query("select * from /.*/ limit 1")

  def construct_query(self):
    _query="select "
    if self.columns is not None:
      _query+=','.join(self.columns)+" from "
    else:
      _query+=" * from "
    _query+= "\""+self.table+"\""
    if self.constraints is not None:
      _query+=" where "
      for index, value in enumerate(self.constraints):
        _query+= value
        if index<len(self.constraints)-1:
          _query+=" and "
      _query+=" "

    if self.limit is not None:
      _query+=" limit " + str(self.limit)
    _query+=";"
    self.logger.debug("Constructing Query: "+_query)
    return self.client.query(_query)[self.table]

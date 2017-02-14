"""
  Constructs the basic queries for the CRT system influxDB.
"""
from influxdb import InfluxDBClient, DataFrameClient
import logging

class BaseQuery:
  """
    Performs the formatting and query construction/issuing for 
    queries to influxDB
  """
  logger = logging.getLogger(__name__)
  _client = DataFrameClient('localhost', 8086, 'root', 'root', 'crt')
  table = "messages"

  @classmethod
  def default_client(cls):
    """
      Utility function for grabbing the default client. 
      Using a static definition this way avoids a LOT of overhead
    """
    return cls._client

  def __init__(self, client=None, columns=None, constraints=None, 
               limit=None, handler=None):
    if client is not None:
      self.client = client
    else:
      self.client = _client
    self.columns = columns
    self.constraints=constraints
    self.limit = limit
    if handler is not None:
      self.logger.addHandler(handler)

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
    try:
      return self.client.query(_query)[self.table].sort_index(axis=0, ascending=False)
    except Exception as e:
      self.logger.error(e)
      self.logger.error(str(self.client.query(_query)))

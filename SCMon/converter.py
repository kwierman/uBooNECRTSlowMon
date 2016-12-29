from epics import ca, caget, caput, PV

class SCConverter:
    db_name="CRT"

  def __init__(self, dataframe, channel):
    self.dataframe = dataframe
    self.channel = channel

  @property
  def epics_name(self):
    return self.db_name+":"+self.channel+".VAL"

  def create_channel(self):
    ca.create_channel(self.epics_name)

  def get(self):
    pass
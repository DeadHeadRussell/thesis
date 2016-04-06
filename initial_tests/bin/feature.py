class Feature():
  TYPE_POINT = 0
  TYPE_AVG = 1
  TYPE_STD = 2

  def __init__(self, name):
    self.name = name
    self.points = {}
    self.avg = []
    self.std = []
  
  def adddata(self, value, data_type, time):
    if data_type == Feature.TYPE_POINT:
      self.addpoint(value, time)
    elif data_type == Feature.TYPE_AVG:
      self.addavg(value)
    elif data_type == Feature.TYPE_STD:
      self.addstd(value)

  def addpoint(self, value, time):
    if time is None and time not in self.points:
      self.points[time] = {'values': []}
    elif time['start'] not in self.points:
      self.points[time['start']] = {'values': [], 'stop': time['stop']}

    if time is None:
      self.points[time]['values'].append(value)
    else:
      self.points[time['start']]['values'].append(value)

  def addavg(self, avg):
    self.avg.append(avg)

  def addstd(self, std):
    self.std.append(std)

  def getpoints(self):
    keys = self.points.keys()
    keys.sort()
    values = []
    for key in keys:
      values.append(self.points[key]['values'][0])
    return {'x': keys, 'y': values}

  def tostring(self):
    return self.name + ' with ' + str(len(self.points)) + ' points'

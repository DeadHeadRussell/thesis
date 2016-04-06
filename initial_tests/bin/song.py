from feature import Feature

class Song():
  def __init__(self, name):
    self.features = {}
    self.name = name

  def getfeatures(self):
    return self.features

  def getfeature(self, name):
    if name not in self.features:
      self.features[name] = Feature(name)
    return self.features[name] 

  def getname(self):
    return self.name

  def tostring(self, deep):
    if not deep:
      return self.name

    feature_strings = [self.features[name].tostring() for name in self.features]
    return self.name + ' - (' + '), ('.join(feature_strings) + ')'

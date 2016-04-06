from __future__ import print_function

import csv
import os
import xml.etree.ElementTree as XML

import matplotlib.pyplot as plt
import numpy

from feature import Feature
from song import Song

def getname(text):
  index = text.find(' Overall Average')
  if index >= 0:
    return text[:index], Feature.TYPE_AVG

  index = text.find(' Overall Standard Deviation')
  if index >= 0:
    return text[:index], Feature.TYPE_STD

  return text, Feature.TYPE_POINT

def loaddata(path):
  iterator = XML.iterparse(path, events=['start', 'end'])

  songs = []
  song = None
  time = None
  feature = None
  data_type = None

  for node in iterator:
    event = node[0]
    element = node[1]

    if event == 'start' and element.tag == 'section':
        time = {'start': float(element.get('start')), 'stop': float(element.get('stop'))}
    elif event == 'end':
      if element.tag == 'data_set_id':
        song = Song(element.text)
        songs.append(song)
      elif element.tag == 'name':
        name, data_type = getname(element.text)
        feature = song.getfeature(name)
      elif element.tag == 'v':
        feature.adddata(float(element.text), data_type, time)
  return songs

def loadscores(path):
  scores = {}
  with open(path) as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:
      scores[row['date']] = row
  return scores
    

def graph(path, name, x1, y1, y2, scale):
  plt.figure()
  if x1 is None:
    plt.plot(y1, 'b', y2, 'r')
  else:
    plt.plot(x1, y1, 'b*', x1, y2, 'r*')
  if scale:
    plt.axis([0, 250, 0, 9])
  plt.ylabel(name)
  plt.savefig(path, bbox_inches='tight')
  plt.close()

def add(data, name, score, avg, std):
  if name not in data:
    data[name] = {'score': [], 'avg': [], 'std': []}
  data[name]['score'].append(score)
  data[name]['avg'].append(avg)
  data[name]['std'].append(std)


def main():
  songs = loaddata('./Fluffhead/feats/all.xml')
  scores = loadscores('./Fluffhead/scores.csv')

  data = {}

  for song in songs:
    song_name = os.path.splitext(song.name.split('\\')[-1])[0]
    features = song.getfeatures()
    score = scores[song_name]

    for name in features:
      if name == 'Score':
        continue

      feature = features[name]
      length = len(feature.avg)
      if length > 13:
        # This is a hack since Running Mean of Area Method of Moments is screwing up
        # and getting a length of 40
        length = 10

      if length > 1:
        for i in range(length):
          add(data, name + ' [' + str(i) + ']', score, feature.avg[i], feature.std[i])
      else:
        add(data, name, score, feature.avg[0], feature.std[0])

  sort = []

  score_types = ['overall', 'rhythm', 'tonal']
  for name in data:
    for score_type in score_types:
      score = [float(d[score_type]) for d in data[name]['score']]
      graph_name = './Fluffhead/corrs/' + name + ' ' + score_type
      graph(graph_name, name + ' ' + score_type, score, data[name]['avg'], data[name]['std'], False)
      avg = numpy.corrcoef(score, data[name]['avg'])[0, 1]
      std = numpy.corrcoef(score, data[name]['std'])[0, 1]
      if not numpy.isnan(avg):
        sort.append({'name': name + ' Avg ' + score_type, 'value': avg})
      if not numpy.isnan(std):
        sort.append({'name': name + ' Std ' + score_type, 'value': std})

  sort = sorted(sort, key = lambda data: abs(data['value']))

  for data in sort:
    print(data['value'], data['name'], sep='\t')

main()


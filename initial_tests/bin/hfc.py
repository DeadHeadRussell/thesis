#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy
import scipy.io.wavfile
import scipy.signal

def get_hfc(audio, window=512, skip=128):
  hfc = []

  # Take just the first channel
  audio = audio[:, 0]

  i = 0
  while (i + window) < len(audio):
    indeces = range(window / 2)
    bins = numpy.abs(numpy.fft.fft(audio[i : i + window]))
    hfc.append(sum(numpy.multiply(indeces, bins[0 : window / 2])))
    i += skip

  return hfc

def get_local_average(values, length=64):
  average = []
  for index in range(len(values)):
    start = max(0, index - length)
    end = min(len(values), index + length + 1)
    average.append(sum(values[start:end]) / (end - start))
  return average

def find_peaks(values):
  peaks = []
  for index, value in enumerate(values):
    if (index != 0 and value > values[index - 1]) and (index != len(values) - 1 and value > values[index + 1]):
      peaks.append(index)
  return peaks
  #return numpy.r_[True, values[1:] < values[:-1]] & numpy.r_[values[:-1] < values[1:], True]

def diff_values(values):
  l = len(values)
  return numpy.subtract(values[1 : l], values[0 : l - 1])

def create_hist(values, indeces, diffs):
  min_bin = min(indeces)
  max_bin = max(indeces)
  hist = [0] * (max_bin - min_bin)
  for i, diff in enumerate(diffs):
    index = indeces[i + 1]
    value = values[index]
    hist[diff - min_bin] += value
  return hist, range(min_bin, max_bin)

def graph(values, name):
  plt.figure()
  plt.plot(values, linewidth=0.1)
  plt.savefig('./' + name + '.png', bbox_inches='tight', dpi=400)
  plt.close()

def graph_histogram(hist):
  plt.figure()
  bins = range(min(hist), max(hist) + 1)
  plot = plt.hist(hist, bins=bins)
  print plot[1]
  print plot[0]
  plt.savefig('./hist.png', bbox_inches='tight', dpi=400)
  plt.close()

def graph_bars(x, y):
  plt.figure()
  plt.bar(x, y)
  print x
  print y
  plt.savefig('./hist.png', bbox_inches='tight', dpi=400)

def main():
  rate, audio = scipy.io.wavfile.read('./Fluffhead/audio/2009_07_31.wav')
  hfc = get_hfc(audio)
  average = get_local_average(hfc, 1024)
  hfcLessAverage = numpy.subtract(hfc, average)
  data = numpy.maximum(hfcLessAverage, numpy.zeros(len(hfcLessAverage)))
  peaks = find_peaks(data)
  diffs = diff_values(peaks)
  hist, bins = create_hist(data, peaks, diffs)

  graph_bars(bins, hist)

  #graph(hfc, 'hfc')
  #graph(average, 'local average')
  #graph(hfcLessAverage, 'hfc - local average')
  #graph(data, 'hfc - local average > 0')
  #graph(data[1024 : 2048], 'chunk')
  #graph_histogram(hist)

main()


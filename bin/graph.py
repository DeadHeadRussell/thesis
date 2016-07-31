# Program to generate graphs of various information related to the features.
# Run `python graph.py -h` to see usage options.

# TODO: Allow caching of all entropy data so it does not have to be
# recalculated every time you want to generate a graph.

import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy
import scipy.io.wavfile
import scipy.signal

import correlate
import entropy

def getDir(output, dirName):
  output_dir = os.path.abspath(os.path.join(output, dirName))
  try:
    os.makedirs(output_dir)
  except OSError:
    if not os.path.isdir(output_dir):
      raise
  return output_dir

def getName(value):
  return os.path.splitext(os.path.basename(value['recording'].name))[0]

def getValue(value, key):
  if 'entropy' in value:
    return value[key]
  if key in value['rhythm']:
    return value['rhythm'][key]
  if key in value['pitch']:
    return value['pitch'][key]

def saveFigure(output_dir, name, callback):
  filename = os.path.join(output_dir, name)
  plt.figure()
  callback(plt)
  plt.savefig(filename + '.png', bbox_inches='tight', dpi=288)
  plt.close()

def plotAudio(plt, recording):
  sampling_rate, audio = scipy.io.wavfile.read(recording.name)
  duration = len(audio) / sampling_rate

  plt.axis([0, duration, -1, 1])

  audio = audio.mean(axis = 1)
  audio /= numpy.max(audio)
  audio = scipy.signal.resample(audio, 12000)
  audio = numpy.asarray(audio, dtype=numpy.double)
  time = numpy.linspace(0, duration, num = len(audio))
  plt.plot(time, audio, 'b')

def generateOnsetLocations(values, output):
  print 'ol'
  output_dir = getDir(output, 'onsets')

  for value in values:
    recording = value['recording']
    onsets = getValue(value, 'onsets')

    def graph(plt):
      plt.title('Onset Locations')
      plt.ylabel('Amplitude')
      plt.xlabel('Time (s)')
      plotAudio(plt, recording)
      for onset in onsets:
        plt.plot([onset, onset], [-1, 1], 'r')

    saveFigure(output_dir, getName(value), graph)

def generateOnsetDiffs(values, output):
  print 'od'
  output_dir = getDir(output, 'diffs')

  for value in values:
    onsets = getValue(value, 'onsets')
    diffs = getValue(value, 'diffs')

    def graph(plt):
      plt.title('Onset Diffs')
      plt.ylabel('Onset Time Difference (s)')
      plt.xlabel('Time (s)')
      graphDiffs = numpy.append(diffs, [0])
      plt.plot(onsets, graphDiffs)

    saveFigure(output_dir, getName(value), graph)

def generateOnsetHistogram(values, output):
  print 'oh'
  output_dir = getDir(output, 'histogram')

  for value in values:
    diffs = getValue(value, 'diffs')

    def graph(plt):
      plt.title('Onset Diff Histogram')
      plt.ylabel('Count')
      plt.xlabel('Onset Time Difference (s)')
      plt.hist(diffs, bins=100, range=(0, 10))#, normed=True)

    saveFigure(output_dir, getName(value), graph)

def generateSmoothedOnsetHistogram(values, output):
  print 'soh'
  output_dir = getDir(output, 'smoothed')

  for value in values:
    diffs = getValue(value, 'diffs')
    hist = getValue(value, 'hist')
    grid = getValue(value, 'grid')

    def graph(plt):
      plt.title('Smoothed Onset Diff Histogram')
      plt.ylabel('Count')
      plt.xlabel('Onset Time Difference (s)')
      bins = plt.hist(diffs, bins=300, normed=True)
      histNorm = hist / numpy.max(hist) * numpy.max(bins[0])
      end = [i for i, v in enumerate(hist) if v > 1e-4][-1]
      plt.plot(grid[:end], histNorm[:end], 'g-')

    saveFigure(output_dir, getName(value), graph)

def generateFrequencySpectrum(values, output):
  print 'fs'
  output_dir = getDir(output, 'frequency')

  for value in values:
    bins = getValue(value, 'bins')
    sampling_rate = getValue(value, 'sampling_rate')

    def graph(plt):
      plt.title('Frequency Spectrum')
      plt.ylabel('Magnitude (dB)')
      plt.xlabel('Frequency')
      grid = numpy.linspace(0, sampling_rate / 2, len(bins))
      plt.axis([0, grid[-1], numpy.min(bins), numpy.max(bins)])
      plt.plot(grid, bins, 'b-')

    saveFigure(output_dir, getName(value), graph)

def generateLoglogSpectrum(values, output):
  print 'llfs'
  output_dir = getDir(output, 'loglog')

  for value in values:
    bins = getValue(value, 'bins')
    sampling_rate = getValue(value, 'sampling_rate')

    def graph(plt):
      plt.title('Loglog Frequency Spectrum')
      plt.ylabel('Magnitude (dB)')
      plt.xlabel('Frequency')
      plt.xscale('log')
      grid = numpy.linspace(0, sampling_rate / 2, len(bins))
      plt.axis([10, grid[-1], numpy.min(bins), numpy.max(bins)])
      plt.plot(grid, bins, 'b-')
    
    saveFigure(output_dir, getName(value), graph)

def generateCorrelation(values, output, ratings_dir, corType):
  output_dir = getDir(output, 'correlation')

  files = [open(os.path.join(ratings_dir, f)) for f in os.listdir(ratings_dir)]
  ratings = correlate.parse_ratings(files)

  entropies = {}
  for value in values:
    song_id = os.path.splitext(os.path.basename(value['recording'].name))[0]
    if 'entropy' in value:
      entropies[song_id] = value['entropy']
    else:
      entropies[song_id] = value[corType]['entropy']

  amRatingsList = []
  amEntropiesList = []
  proRatingsList = []
  proEntropiesList = []

  for rating in ratings:
    song_id = rating['song_id']
    if int(song_id) < 22:
      amRatingsList.append(rating['value'])
      amEntropiesList.append(entropies[song_id])
    else:
      proRatingsList.append(rating['value'])
      proEntropiesList.append(entropies[song_id])

  entropiesList = amEntropiesList + proEntropiesList
  fit = numpy.poly1d(numpy.polyfit(entropiesList, amRatingsList + proRatingsList, 1))

  def graph(plt):
    plt.title('Correlation (' + corType + ')')
    plt.ylabel('Ratings')
    plt.xlabel('Entropies')
    plt.plot(proEntropiesList, proRatingsList, 'bo', label = 'Professional')
    plt.plot(amEntropiesList, amRatingsList, 'rs', label = 'Amateur')
    plt.plot(numpy.mean(proEntropiesList), numpy.mean(proRatingsList), 'gv', label = 'Pro')
    plt.plot(numpy.mean(amEntropiesList), numpy.mean(amRatingsList), 'y^', label = 'Ama')
    plt.plot(entropiesList, fit(entropiesList), 'black')
    plt.legend(('Pro', 'Ama', 'Pro Mean', 'Ama Mean'), numpoints = 1)

  saveFigure(output_dir, corType, graph)

def generateRhythmCorrelation(values, output, ratings_dir):
  print 'rc'
  generateCorrelation(values, output, ratings_dir, 'rhythm')

def generatePitchCorrelation(values, output, ratings_dir):
  print 'pc'
  generateCorrelation(values, output, ratings_dir, 'pitch')

rhythm_keys = ['onset_locations', 'onset_diffs', 'onset_histogram', 'smooth_onset_histogram', 'rhythm_correlation']
pitch_keys = ['frequency_spectrum', 'loglog_spectrum', 'pitch_correlation']

def parseArgs():
  parser = argparse.ArgumentParser(description='Graph various information related to the entropy features')
  parser.add_argument('-o', '--output', metavar='<output file>', required=True, type=str, help='Folder to output graphs to.')
  parser.add_argument('-l', '--onset-locations', action='store_true', help='Graph the locations of onsets overlaying the waveform')
  parser.add_argument('-d', '--onset-diffs', action='store_true', help='Graph of the onset timing diffs over time of the audio recording')
  parser.add_argument('-g', '--onset-histogram', action='store_true', help='Histogram of the onset diffs')
  parser.add_argument('-p', '--smooth-onset-histogram', action='store_true', help='Parzen smootehd onset diff histogram')
  parser.add_argument('-f', '--frequency-spectrum', action='store_true', help='Frequency spectrum of audio recording')
  parser.add_argument('-s', '--loglog-spectrum', action='store_true', help='Loglog frequency spectrum of audio recording')
  parser.add_argument('-r', '--rhythm-correlation', action='store_true', help='Graph the correlation between the ratings and the rhythm entropies')
  parser.add_argument('-c', '--pitch-correlation', action='store_true', help='Graph the correlation between the ratings and the pitch entropies')
  parser.add_argument('-u', '--ratings-dir', metavar='<ratings dir>', type=str, help='Directory that contains the user ratings and optionally the entropies cache. Required when -r or -c are specified')
  parser.add_argument('files', metavar='recordings', nargs='+', type=argparse.FileType('r'), help='Audio recordings to process')
  return parser.parse_args()

def main():
  args = parseArgs()
  
  argsDict = vars(args)
  norhythm = not reduce(lambda accum, key: accum or argsDict[key], rhythm_keys, False)
  nopitch = not reduce(lambda accum, key: accum or argsDict[key], pitch_keys, False)

  if (args.rhythm_correlation or args.pitch_correlation) and not args.ratings_dir:
    print >> sys.stderr, 'Cache dir is not provided for the ratings'
    exit(-1)

  values = entropy.run(args.files, norhythm = norhythm, nopitch = nopitch)
  
  if args.onset_locations:
    generateOnsetLocations(values, args.output)

  if args.onset_diffs:
    generateOnsetDiffs(values, args.output)

  if args.onset_histogram:
    generateOnsetHistogram(values, args.output)

  if args.smooth_onset_histogram:
    generateSmoothedOnsetHistogram(values, args.output)

  if args.frequency_spectrum:
    generateFrequencySpectrum(values, args.output)

  if args.loglog_spectrum:
    generateLoglogSpectrum(values, args.output)

  if args.rhythm_correlation:
    generateRhythmCorrelation(values, args.output, args.ratings_dir)

  if args.pitch_correlation:
    generatePitchCorrelation(values, args.output, args.ratings_dir)

if __name__ == '__main__':
  main()


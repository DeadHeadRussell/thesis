# This file computes the entropy values for audio recordings.
# Run `python entropy.py -h` for more info / usage.

import argparse
import logging
import subprocess 
import sys

import matplotlib.pyplot as plt
import numpy
import scipy.io.wavfile
import scipy.stats

logging.basicConfig()
logging.addLevelName(0, 'Debug')
logging.addLevelName(1, 'Progress')
logging.addLevelName(2, 'Info')
logger = logging.getLogger('entropy')
logger.setLevel(3)

def parseArgs():
  parser = argparse.ArgumentParser(description='Compute the rhythm and pitch entropies of audio recordings')
  parser.add_argument('-o', '--output', metavar='<output file>', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='File to output to (defaults to stdout)')
  parser.add_argument('-r', '--rhythm', dest='nopitch', action='store_true', help='Calculate only the rhythm entropies')
  parser.add_argument('-p', '--pitch', dest='norhythm', action='store_true', help='Calculte only the pitch entropies')
  parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level for logging output (default: no logging)')
  parser.add_argument('files', metavar='recordings', nargs='+', type=argparse.FileType('r'), help='Audio recordings to process')
  return parser.parse_args()

def compute_rhythm(recording):
  onsets_string = subprocess.check_output(['aubioonset', '-i', recording.name])
  onsets = onsets_string.strip().split('\n')
  onsets = [float(onset) for onset in onsets]
  diffs = numpy.abs(numpy.diff(onsets))
  grid = numpy.linspace(0, 10, 1000)
  density = scipy.stats.gaussian_kde(diffs)
  hist = density(grid)
  entropy = scipy.stats.entropy(hist)

  logger.log(1, '%s rhythm %f', recording.name, entropy)
  return {
      'entropy': entropy,
      'recording': recording,
      'onsets': onsets,
      'diffs': diffs,
      'hist': hist,
      'grid': grid
  }

def compute_pitch(recording):
  sampling_rate, audio = scipy.io.wavfile.read(recording)
  audio = audio.mean(axis=1)
  audio = numpy.asarray(audio, dtype=numpy.double)
  audio /= numpy.max(audio)

  fft_size = 64000
  jump = fft_size / 2
  i = 0

  bins = numpy.zeros(fft_size / 2)

  while i < len(audio):
    process = audio[i : i + fft_size]
    process *= numpy.hamming(len(process))
    fft = numpy.fft.rfft(process, n=fft_size - 1)
    bins = numpy.add(bins, numpy.abs(fft))
    i += jump

  bins /= numpy.sum(bins)
  bins = [20 * numpy.log10(x) for x in bins]

  linspace = numpy.linspace(1, sampling_rate / 2, fft_size / 2)
  logspace = numpy.logspace(0, numpy.log10(sampling_rate / 2), 10000, base=10)
  loglogbins = numpy.interp(logspace, linspace, bins)

  entropy = scipy.stats.entropy(loglogbins)

  logger.log(1, '%s pitch %f', recording.name, entropy)
  return {
      'entropy': entropy,
      'recording': recording,
      'sampling_rate': sampling_rate,
      'bins': bins,
      'loglogbins': loglogbins
  }

def compute_both(recording):
  return {
      'recording': recording,
      'rhythm': compute_rhythm(recording),
      'pitch': compute_pitch(recording)
  }

def run(files, nopitch = False, norhythm = False):
  logger.log(2, 'Working with %d files', len(files))

  if nopitch:
    logger.log(2, 'Computing only rhythm entopies')
    return map(lambda recording: compute_rhythm(recording), files)
  if norhythm:
    logger.log(2, 'Computing only pitch entopies')
    return map(lambda recording: compute_pitch(recording), files)
  logger.log(2, 'Computing both rhythm and pitch entopies')
  return map(lambda recording: compute_both(recording), files)

def output(values, output):
  logger.log(2, 'Writing data')
  for value in values:
    if 'entropy' in value:
      output.write(value['recording'].name)
      output.write('\t')
      output.write(str(value['entropy']))
      output.write('\n')
    else:
      output.write(value['recording'].name)
      output.write('\t')
      output.write(str(value['rhythm']['entropy']))
      output.write('\t')
      output.write(str(value['pitch']['entropy']))
      output.write('\n')

if __name__ == '__main__':
  args = parseArgs()
  logger.setLevel(3 - min(args.verbose, 3))
  values = run(args.files, nopitch = args.nopitch, norhythm = args.norhythm)
  output(values, args.output)
  

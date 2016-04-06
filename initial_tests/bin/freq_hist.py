import math

import numpy
import scipy.stats
import scipy.io.wavfile

def compute(data):
  density = scipy.stats.gaussian_kde(data)
  grid = numpy.linspace(min(data), max(data), 100)
  return scipy.stats.entropy(density(grid))

file_names = []
with open('survey.txt') as files:
  file_names = files.read().split('\n')
  print 'Working with ' + str(len(file_names) - 2) + ' files'

input_dir = file_names[0]
output_dir = file_names[1] + 'frequency/'
output_file = output_dir + 'entropy.txt'

entropies = []

for i in range(2, len(file_names)):
  file_name = file_names[i]
  if len(file_name) == 0:
    continue

  sampling_rate, audio = scipy.io.wavfile.read(input_dir + file_name + '.wav')
  audio = audio.mean(axis=1)
  audio = numpy.asarray(audio, dtype=numpy.double)
  audio /= numpy.max(audio)

  jump = sampling_rate / 2
  i = 0

  bins = numpy.zeros(sampling_rate / 2)

  while i < len(audio):
    process = audio[i : i + sampling_rate]
    process *= numpy.hamming(len(process))
    fft = numpy.fft.rfft(process, n=sampling_rate-1)
    bins = numpy.add(bins, numpy.abs(fft))
    i += jump

  bins /= numpy.sum(bins)
  entropy = compute(bins)

  entropies.append({
    'file_name': file_name,
    'value': entropy,
    'bins': bins
  })
  print entropy

print 'writing output...'
with open(output_file, 'w') as out:
  for entropy in entropies:
    out.write(entropy['file_name']);
    out.write('\t')
    out.write(str(entropy['value']))
    out.write('\n')

print 'computing graphs...'

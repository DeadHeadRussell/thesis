import subprocess 

import matplotlib.pyplot as plt
import modal
import modal.onsetdetection as od
import numpy
import scipy.stats
import scipy.io.wavfile

# How many onsets to diff against.
mergebands = True

def compute(data, title):
  diffs = []
  for i in range(len(data)):
    index = i - 1
    if index >= 0:
      diffs.append(data[i] - data[index])

  diffs = numpy.abs(numpy.fft.rfft(data))
  density = scipy.stats.gaussian_kde(diffs)
  diffs_grid = numpy.linspace(min(diffs), max(diffs), 100)

  print len(diffs)

  plt.figure()
  plt.title(title)
  #plt.hist(diffs, bins=range(min(diffs), max(diffs), 500), normed=True)
  #plt.hist(diffs)
  plt.plot(diffs_grid, density(diffs_grid), 'r-')
  #plt.plot(diffs, 'r-')
  plt.savefig('../' + title + '.png')
  plt.close()

  #return scipy.stats.entropy(density(diffs_grid))
  return scipy.stats.entropy(diffs)

def addpoints(data, points):
  if len(points):
    data.append(sum(points) / len(points))
  points[:] = []

def parse(onsets):
  curr_band = -1
  data = []
  for onset in onsets:
    if len(onset) == 0:
      continue
    frame = onset.split(' ')[0]
    band = onset.split(' ')[1]
    if band != curr_band and curr_band >= 0 and not mergebands:
      yield compute(data)
      data = []
    curr_band = band
    data.append(int(frame))

  if mergebands:
    data.sort()
    newdata = []
    points = []
    for p in data:
      if len(points) == 0 or p - points[-1] > 2:
        addpoints(newdata, points)
      points.append(p)

    addpoints(newdata, points)
    data = newdata

  yield compute(data)

file_names = []
with open('survey.txt') as files:
  file_names = files.read().split('\n')
  print 'Working with ' + str(len(file_names) - 2) + ' files'

input_dir = file_names[0]
output_dir = file_names[1]
output_file = output_dir + 'entropy.txt'

with open(output_file, 'w') as out:
  for i in range(2, len(file_names)):
    file_name = file_names[i]
    if len(file_name) == 0:
      continue

    """
        onset_string = subprocess.check_output(['./onsets', input_dir + file_name + '.wav'])
        onsets = onset_string.split('\n')
          data = parse(onsets)
    """

    sampling_rate, audio = scipy.io.wavfile.read(input_dir + file_name + '.wav')
    audio = audio.mean(axis=1)
    audio = numpy.asarray(audio, dtype=numpy.double)
    audio /= numpy.max(audio)

    odf = modal.ComplexODF()
    odf.set_hop_size(256)
    odf.set_frame_size(256)
    odf.set_sampling_rate(sampling_rate)
    odf_values = numpy.zeros(len(audio) / odf.get_hop_size(), dtype=numpy.double)
    odf.process(audio, odf_values)

    onset_det = od.OnsetDetection()
    onset_det.peak_size = 3
    onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()
    entropy = compute(onsets, file_name)

    out.write(file_name);
    out.write('\t')
    out.write(str(entropy))
    out.write('\n')



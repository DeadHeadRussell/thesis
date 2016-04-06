import subprocess 

import aubio
import matplotlib.pyplot as plt
import modal
import modal.onsetdetection as od
import numpy
import scipy.stats
import scipy.io.wavfile

mergebands = True

def compute(data, title):
  diffs = numpy.abs(numpy.diff(data))
  #diffs = data
  #diffs = [d[1] for d in data]
  #diffs = numpy.abs(numpy.fft.rfft(data))

  density = scipy.stats.gaussian_kde(diffs)
  diffs_grid = numpy.linspace(-0.2, 0.2, 100)
  hist = density(diffs_grid)
  hist /= numpy.max(hist)

  entropy = scipy.stats.entropy(hist)
  #entropy = scipy.stats.entropy(diffs)

  plt.figure()
  plt.title(title + ' - ' + str(entropy))
  #plt.hist(diffs, bins=500, normed=True)
  plt.plot(diffs_grid, hist, 'r-')
  #plt.plot(diffs, 'r-')
  #x = [d[0] for d in data]
  #plt.plot(x, diffs, 'r-')
  plt.savefig('../' + title + '.png')
  plt.close()

  return entropy

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

    sampling_rate, audio = scipy.io.wavfile.read(input_dir + file_name + '.wav')
    audio = audio.mean(axis=1)
    audio = numpy.asarray(audio, dtype=numpy.double)
    audio /= numpy.max(audio)

    odf = modal.ComplexODF()
    odf.set_hop_size(512)
    odf.set_frame_size(1024)
    odf.set_sampling_rate(sampling_rate)
    odf_values = numpy.zeros(len(audio) / odf.get_hop_size(), dtype=numpy.double)
    odf.process(audio, odf_values)

    onset_det = od.OnsetDetection()
    onset_det.peak_size = 3
    onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()
    entropy = compute(onsets, file_name)

    """
    onsets_string = subprocess.check_output(['aubioonset.exe', '-i', input_dir + file_name + '.wav'])
    onsets = onsets_string.strip().split('\n')
    onsets = [float(onset) for onset in onsets]
    entropy = compute(onsets, file_name)
    """

    """
    source_func = aubio.source(input_dir + file_name + '.wav', 44100, 512)
    tempo_func = aubio.tempo('specdiff', 1024, 512, 44100)

    avgList = []
    output = []
    beatsSum = 0
    last = 0

    beats = []
    while True:
      samples, read = source_func()
      is_beat = tempo_func(samples)
      if is_beat:
        sample = tempo_func.get_last_s()
        beats.append(sample)

        if last > 0:
          avgList.append(sample - last)
          if len(avgList) > 16:
            avgList.pop(0)
          avg = sum(avgList) / len(avgList)
          beatsSum += avg
          output.append((sample, avg))
        last = sample

      if read < 512:
        break
    """

    """
    base = beatsSum / len(output)
    data = [(d[0], d[1] - base) for d in output]
    entropy = compute(data, file_name)
    """

    """
    bpms = 60 / numpy.diff(beats)
    deviation = numpy.subtract(bpms, numpy.median(bpms))
    entropy = compute(numpy.abs(deviation), file_name)
    """

    print entropy

    out.write(file_name);
    out.write('\t')
    out.write(str(entropy))
    out.write('\n')


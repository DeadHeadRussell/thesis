# This file correlates the entropies with the user ratings following these steps:
# 1. Calculte the rhythm and pitch entropies (caches the results)
# 2. Processes the user ratings (caches the results)
# 3. Correlates the rhythm entropies against the user ratings
# 4. Correlates the pitch entropies against the user ratings

import os
import sys

import numpy
import scipy.stats

import entropy

def parse_ratings(files):
  ratings = {}
  for f in files:
    songs = []
    for line in f.readlines():
      values = line.strip().split()
      songs.append({'id': values[0], 'value': int(values[1])})

    rating_values = [song['value'] for song in songs]
    avg = numpy.mean(rating_values)
    std = numpy.std(rating_values)

    for song in songs:
      ratings[song['id']] = ratings.get(song['id'], [])
      ratings[song['id']].append((song['value'] - avg) / std)
  
  return [{
    'song_id': song_id,
    'value': numpy.mean(ratings[song_id])
  } for song_id in ratings]

def output_ratings(ratings, output):
  for rating in ratings:
    output.write(rating['song_id'])
    output.write('\t')
    output.write(str(rating['value']))
    output.write('\n')

def run():
  if len(sys.argv) != 4 and len(sys.argv) != 5:
    print >> sys.stderr, 'Usage: ./correlate <recordings dir> <ratings dir> <results dir> [<exclude>]'
    exit(-1)

  clipsdir = sys.argv[1]
  ratingsdir = sys.argv[2]
  resultsdir = sys.argv[3]

  exclude = []
  if len(sys.argv) == 5:
    with open(sys.argv[4]) as exclude_file:
      for line in exclude_file.readlines():
        exclude.append(line.strip())

  entropies_results = os.path.join(resultsdir, 'entropies.txt')
  ratings_results = os.path.join(resultsdir, 'ratings.txt')

  if not os.path.isfile(entropies_results):
    print 'Calculating entropies'

    files = [open(os.path.join(clipsdir, f)) for f in os.listdir(clipsdir)]
    entropy.logger.setLevel(1)
    values = entropy.run(files)
    entropy.output(values, open(entropies_results, 'w'))

  print 'Parsing entropies'
  entropies = {}
  with open(entropies_results) as inputfile:
    for line in inputfile.readlines():
      values = line.strip().split('\t')
      song_id = os.path.splitext(os.path.basename(values[0]))[0]
      entropies[song_id] = {
          'rhythm': float(values[1]),
          'pitch': float(values[2])
      }

  if not os.path.isfile(ratings_results):
    print 'Calculating ratings'
    files = [open(os.path.join(ratingsdir, f)) for f in os.listdir(ratingsdir)]
    ratings = parse_ratings(files)
    output_ratings(ratings, open(ratings_results, 'w'))

  print 'Parsing ratings'
  ratings = {}
  with open(ratings_results) as inputfile:
    for line in inputfile.readlines():
      values = line.strip().split('\t')
      ratings[values[0]] = {'rating': float(values[1])}

  ordered_rhythms = []
  ordered_pitches = []
  ordered_ratings = []

  for song_id in entropies:
    if song_id not in exclude:
      ordered_rhythms.append(entropies[song_id]['rhythm'])
      ordered_pitches.append(entropies[song_id]['pitch'])
      ordered_ratings.append(ratings[song_id]['rating'])

  rhythm_entropy = scipy.stats.pearsonr(ordered_rhythms, ordered_ratings)
  pitch_entropy = scipy.stats.pearsonr(ordered_pitches, ordered_ratings)

  print 'Rhythm correlation'
  print rhythm_entropy
  print 'Pitch correlation'
  print pitch_entropy

if __name__ == '__main__':
  run()


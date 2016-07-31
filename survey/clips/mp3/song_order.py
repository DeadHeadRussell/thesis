from __future__ import print_function
import random

a_songs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 18, 20, 21]
b_songs = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 38, 40, 41, 42]

def create_order(number_songs):
  sampled_a = random.sample(a_songs, number_songs / 2)
  sampled_b = random.sample(b_songs, number_songs - len(sampled_a))

  for i in range(number_songs):
    if (random.randint(0, 1) is 0 and len(sampled_a) > 0) or len(sampled_b) == 0:
      yield sampled_a.pop()
    else:
      yield sampled_b.pop()

if __name__ == '__main__':
  with file('./song_ratings.txt', 'w') as out:
    for number in create_order(20):
    #for number in create_order(len(a_songs) + len(b_songs)):
      print('{:0>2d}'.format(number), 'X', sep='\t', file=out)


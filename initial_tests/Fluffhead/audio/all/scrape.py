#!/usr/bin/env python

# This file downloads all fan recordings of Fluffhead by Phish
# The usage of the songs is in accordance with Phish's fan Taping Policy

import json
import time
import urllib2

song_name = 'fluffhead'
song_url = 'http://www.phishtracks.com/api/v1/songs/' + song_name
while True:
  try:
    print 'Fetching: ' + song_url
    song_data = json.loads(urllib2.urlopen(song_url).read())
    break
  except urllib2.HTTPError as e:
    print e
    time.sleep(1)
print 'Got ' + str(len(song_data['tracks'])) + ' tracks'

for index, track in enumerate(song_data['tracks']):
  if index <= 184:
    continue

  time.sleep(0.5)

  url = 'http://assets.phishtracks.com/' + track['file_url']
  print 'Downloading: ' + track['show']['show_date']
  req = urllib2.urlopen(url)
  CHUNK = 16 * 1024
  filename = track['show']['show_date'].replace('-', '_') + '.mp3'
  with open(filename, 'wb') as fp:
    while True:
      chunk = req.read(CHUNK)
      if not chunk: break
      fp.write(chunk)

print 'done'


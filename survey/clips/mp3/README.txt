CONTENTS
============

In this zip folder, there should be 39 mp3 files (labelled 01.mp3 - 42.mp3,
with 16, 36, 37 missing). There is also this one README.txt file and a
song_order.py file.

PREAMBLE
============

The purpose of this is to rate a number of the mp3 files in this folder from
1-5 based on the skill level of the performance.  The scale is as follows:
5 - Flawless performance
4 - Minor mistakes that do not detract from the performance
3 - Many mistakes that do not detract from the performance
2 - Many mistakes that detract from the performance
1 - More mistakes than playing; hard to listen to

First, we will have you listen to three example songs along with their
suggested ratings to get you accustomed to the scale.

Second, we will have you generate a list of numbers which correspond to the
order that you will rate the songs in.  You will only be rating a subset of
these songs.

Third, we will have you listen to each song in order of the list and mark
down the rating of that song on the 1-5 scale noted above.

NOTES
============

While listening to the performances, keep in mind that we are not interested
in the skill of the editing and mastering of the performance, only of the
ability to perform the instruments.  This involves the rhythm, intonation,
etc of the instruments.  We have encoded the songs as low quality mp3 files
to attempt to adjust for this, but it is not perfect.

INSTRUCTIONS
============

Listen to the following songs in order.  Their recommended ratings are
supplied in the right hand column.

39.mp3     5
19.mp3     3
15.mp3     1

Run `python song_order.py`.  You should now have a file song_ratings.txt in
your folder. Open up this file.  There are two columns.  The left hand column
has the song number to listen to while the right hand column has an "X".
Listen to each song in order of the song_ratings.txt file and replace each
"X" with your rating of the song.

When you have completed rating each song, email me the song_ratings.txt file.

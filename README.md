# Automatic Detection of Musical Ability #

Music and Tech Masters thesis at CMU.

This repository contains the code to extract the rhythm and pitch features
introduced in the thesis. It also contains programs to correlate feature
vectors to test how usefule the features are, and graphing utilities to provide
insight into the different steps of extracting the features.

This repository also contains all the data required to reproduce the results
found in the thesis and all code / data that was used to help discover /
develop the features.

Layout of the repo:
* `/bin`: All code related to extracting and testing the features
* `/survey`: All data requried to reproduce the results of the thesis
* `/initial_tests`: All previous related work thrown into one folder

## Running the code ##

### Dependencies ###

* [python 2.X](https://www.python.org/)
* [aubioonsets](http://aubio.org/)

This code has been only tested on cygwin on Windows, but it should work on
other systems.

### entropy.py ###

To extract the rhythm and pitch features from a set of audio recordings, run:
`python ./bin/entropy.py /path/to/audio/*.wav > results.txt`
See its help output for more useage info:
`python ./bin/entropy.py -h`

This script currently supports just wav files.

### correlate.py ###

To correlate the entropies of a set of audio files with the ratings from a set
of users, run:
`python ./bin/correlate.py /path/to/audio /path/to/ratings /path/to/results_cache [ /path/to/exclude_files ]`
This script will compute the entropies of the audio files, preprocess the
ratings, cache the results (to save time on future executions), then outputs
the results to `stdout`. See the `/survey` folder for the proper format of the
required and optional files.

It will only re-compute the entropy values and re-process the ratings if the
cache files do not exist in the supplied cache folder. If you wish to update
one, or both, of those values, simply delete the associated file(s).


### graph.py ###

Outputs various graphs to provide insight of the features.
Run `python ./bin/graph.py -h` to see useage details.
See `./survey/graph.sh` to see and example use of it.

## Survey Results ##

To reproduce the survey results, run `./survey/run.sh`. If you can't run sh,
files, all it does is run the following line: (assuming the cwd is './survey`)
`python ../bin/correlate.py ./clips/wav ./ratings ./results`

### Audio ###

All audio files, including the original files, the shortened files, and the
shortened mp3 files used in the survey. These files are located in the
`./survey/clips` folder. `survey.zip` contains all audio / instructions
required to send to any survey takers. It is simply a zip of the
`./survey/clips/mp3` folder.

The filename of each song int he `./survey/wav` and the `./survey/mp3` folders
is the `song_id`.

### Ratings ###

`./survey/ratings` contains all the ratings used in the thesis. Each text file
contains the ratings from a single rater. Each line is the `song_id` followed
by a tab followed by the rating from 1-5.

### Results / Graphs ###

After running the script to reproduce the results, the `./survey/results`
folder contains the cache of the song entropies and the and processed
song ratings. The script output's to stdout the correlation values.

Run `./survey/graph.sh` to regenerate all graphs associated with the survey
(you can already find the graphs in the `./survey/graphs` folder). This script
takes a while to run as is, so you may want to run `./bin/graph.py` with your
own options.


## Initial Tests ##

A mess of previous relted work. Feel free to poke around, and if you have any
questions, shoot me an email / create an issue on github and I may still
remember what's in that folder...



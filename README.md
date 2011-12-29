aget - An Amazon Cloud Player Download Utility
================================================================================

Usage
--------------------------------------------------------------------------------

From your [Cloud Player](https://www.amazon.com/gp/dmusic/mp3/player) select the
sounds you want and click the _Download_ button. You'll download an playlist
file (extention amz). Then run aget!

    aget.py Amazon-MP3-*.amz

By default this will download all the songs to ~/Music but can be changed with
the `-O` option:

    aget.py -O /scratch/music Amazon-MP3-*.amz


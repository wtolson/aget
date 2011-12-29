#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'William Trevor Olson'
__email__ = 'trevor@heytrevor.com'
__license__ = 'GPLv3'
__version__ = '1.0.0'

import sys
from os import path, makedirs
from urllib import urlretrieve
from argparse import ArgumentParser
from lxml import etree
from pprint import pprint
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed


def noop(*args, **kwargs):
    """Because less is more..."""
    pass


class Track(object):
    def __init__(self, track_node):
        if track_node.tag != 'track':
            raise Exception('Must be initialized with a track node!')

        self.node = track_node
        self._cache = {}

    def _get_prop(self, name):
        if name not in self._cache:
            prop = self.node.find(name)

            if prop is not None:
                self._cache[name] = prop.text
            else:
                self._cache[name] = None
        
        return self._cache[name]

    @property
    def location(self):
        return self._get_prop('location')

    @property
    def creator(self):
        return self._get_prop('creator')

    @property
    def album(self):
        return self._get_prop('album')

    @property
    def title(self):
        return self._get_prop('title')

    @property
    def image(self):
        return self._get_prop('image')

    @property
    def duration(self):
        return self._get_prop('duration')

    @property
    def trackNum(self):
        return self._get_prop('trackNum')

    @property
    def meta(self):
        if not hasattr(self, '_meta'):
            self._meta = {}
            for prop in self.node.findall('meta'):
                name = prop.get('rel')[29:]
                value = prop.text
                self._meta[name] = value

        return self._meta


    def make_filename(self, base='', full=True):
        """Create a filename based on the tracks meta data."""
        if self.trackNum:
            name = '{} - {}'.format(self.trackNum.rjust(2, '0'), self.title)
        else:
            name = self.title

        name = '{}.{}'.format(name, self.meta.get('trackType', 'mp3'))

        if full:
            name = path.join(self.creator or 'Unknown', self.album or 'Unknown', name)

        return path.join(base, name)

    def _on_progress(self, blocknum, blocksize, totalsize):
        self.pbar.maxval = totalsize
        if blocknum*blocksize < totalsize:
            self.pbar.update(blocknum*blocksize)
        else:
            self.pbar.update(totalsize)

    
    def download(self, out_dir='', filename=None, show_progress=True):
        if filename is None:
            filename = self.make_filename(base=out_dir)

        if show_progress:
            widgets = [Percentage(), ' ', Bar(), ' ', ETA(), ' ', FileTransferSpeed()]
            self.pbar = ProgressBar(widgets=widgets)
            try:
                self.pbar.maxval = int(self.meta.get('fileSize'))
            except:
                pass

            reporthook = self._on_progress

            self.pbar.start()
        else:
            reporthook = noop

        try:
            makedirs(path.dirname(filename))
        except OSError as err:
            if err.errno != 17: # File already exists
                print '{}: {}'.format(err.strerror, err.filename)
                sys.exit(err.errno)

        urlretrieve(self.location, filename=filename, reporthook=reporthook)

        if show_progress:
            self.pbar.finish()
    


class Playlist(object):
    def __init__(self, amz_doc):
        if hasattr(amz_doc, 'read'):
            amz_doc = amz_doc.read()

        self.dom = etree.fromstring(amz_doc)

        if self.dom.tag != 'playlist':
            raise Exception('Invalid Playlist Doc!')

    @property
    def title(self):
        if not hasattr(self, '_title'):
            title = self.dom.find('title')
            if title is not None:
                self._title = title.text
            else:
                self._title = None

        return self._title

    @property
    def tracks(self):
        if not hasattr(self, '_tracks'):
            self._tracks = [Track(track) for track in self.dom.xpath('/playlist/trackList/track')]

        return self._tracks


def main():
    parser = ArgumentParser(description='Download your amazon music.')

    parser.add_argument('playlist', metavar='PLAYLIST', type=file,
                        help='an amazon playlist file')

    parser.add_argument('-O', '--output', default='~/Music',
                        help='the root file to save your music')

    try:
        args = parser.parse_args()
    except IOError as err:
        print '{}: {}'.format(err.strerror, err.filename)
        sys.exit(err.errno)


    # Parse the playlist file
    try:
        playlist = Playlist(args.playlist)
        tracks = playlist.tracks
        total_tracks = len(tracks)

        print 'Found {} tracks...'.format(total_tracks)
    except:
        print 'Invalid playlist file'
        sys.exit(1)


    # Create the output directory
    out_dir = path.abspath(path.expanduser(args.output))
    try:
        makedirs(out_dir)
    except OSError as err:
        if err.errno != 17: # File already exists
            print '{}: {}'.format(err.strerror, err.filename)
            sys.exit(err.errno)

    # Download each track
    for track_num, track in enumerate(tracks, 1):
        print 'Downloading {} of {}: {}...'.format(track_num, total_tracks, track.title)
        track.download(out_dir=out_dir)
    
    print 'Finished!'



if __name__ == '__main__':
    main()

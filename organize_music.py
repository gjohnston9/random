"""
I wanted to convert my Google Play Music library to Plex, so I needed to download my library and then upload to my
Plex server. But GPM download places all my songs in a single unorganized directory, so I needed to organize the songs
by artist and album title. This script accomplishes that.
"""

import os
import shutil

from collections import defaultdict, namedtuple

from mutagen.easyid3 import EasyID3

input_dir = r"D:\Users\greg9381\Music\Google Play backup April 2019"
output_dir = r"D:\Users\greg9381\Music\plex test"

song_info = namedtuple('SongInfo', ['song', 'path'])
music = defaultdict(lambda: defaultdict(list)) # { artist: {album: {song_info_list}}}
# If the case of the album title varies between songs in the same album, use this dict to keep the album case specified
# in the first song we encountered
artist_to_lowercase_albums = defaultdict(dict) # { artist: {lowercase_album_name: original_album_name }}
# Similarly, use the case of the first time an artist was encountered, if the artist case varies between songs
lowercase_artist_to_artist = dict()

# for some reason, some artists show up like "artist name/artist name". Fix it with a hack and keep track of it here
trimmed_artists = list() 
changed_album_names = set()
album_replacements = {
	'/': 'SLASH',
	':': 'COLON',
	'..': 'DOTDOT',
	'?': 'QUESTION_MARK',
	'*': 'STAR',
	'>': 'GREATER_THAN',
	'<': 'LESS_THAN',
	'|': 'PIPE',
}

for f in os.listdir(input_dir):
	song = EasyID3(os.path.join(input_dir, f))
	title = song['title']
	artist = song['artist']
	album = song['album']
	assert len(title) == 1
	assert len(artist) == 1
	assert len(album) == 1
	title = title[0].strip()
	artist = artist[0].strip()
	album = album[0].strip()

	if '/' in artist:
		artist = artist.split('/')[0]
		trimmed_artists.append((song, artist))
	if artist.lower() not in lowercase_artist_to_artist:
		lowercase_artist_to_artist[artist.lower()] = artist
	else:
		artist = lowercase_artist_to_artist[artist.lower()] # normalize artist case across songs

	for before, after in album_replacements.items():
		if before in album:
			album = album.replace(before, after)
			changed_album_names.add((album, artist))
	if album.lower() not in artist_to_lowercase_albums[artist]:
		artist_to_lowercase_albums[artist][album.lower()] = album
	else:
		album = artist_to_lowercase_albums[artist][album.lower()] # normalize album case between songs
	music[artist][album].append(song_info(song, f))

try:
	for artist, albums in music.items():
		print("Artist: %s" % artist)
		print("Albums:")
		for album, songs in albums.items():
			print("\talbum: %s" % album)
			print("\t\tsongs:")
			for song in songs:
				print("\t\t\t%s" % song.path)
		os.mkdir(os.path.join(output_dir, artist))
		for album, songs in albums.items():
			os.mkdir(os.path.join(output_dir, artist, album))
			for song in songs:
				try:
					source_file = os.path.join(input_dir, song.path)
					dest_dir = os.path.join(output_dir, artist, album)
					shutil.copy(source_file, dest_dir)
				except:
					print("failed to copy from %s to %s" % (source_file, dest_dir))
					print("song:")
					print(song)
					raise
finally:
	for song, new_artist in trimmed_artists:
		print("**Warning: shortened artist for song: %s from %s to %s" %
			  (song['title'][0], song['artist'][0], new_artist))
	for album, artist in changed_album_names:
		print("**Warning: replaced characters in album name: %s by artist: %s" % (album, artist))
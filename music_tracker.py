# ----------------------------------------------------------------------

# Program:     Trending Music Tracker
# Purpose:     Use a web scraper on the Pitchfork website to get
#              the names of music artists releasing new music.
#              Assess their popularity on Twitter using the Twitter API.
#
# Author:       Justin Singh
#
# ----------------------------------------------------------------------
"""
Implements a web scraper for the website https://pitchfork.com and
gets the names of music artists releasing new music. Measures the
current twitter popularity of these music artists using the Twitter API.
"""
import json
from bs4 import BeautifulSoup
import requests

# global variables
BASE_URL = "https://pitchfork.com"

def get_new_tracks():
    """
    Scrapes Pitchfork for newly released tracks and returns a dictionary
    of those tracks and the artists who made them.

    :return: (dictionary) key = music artist, value = newly released
            track(s) (list of strings)
    """
    # music dictionary that maps artist names to new music titles
    music_dict = {}

    for i in range(1, 4):
        # web page we are using to find newly released music
        new_music_page = requests.get(BASE_URL + "/reviews/tracks/?page=" +
                                      str(i))

        soup = BeautifulSoup(new_music_page.text, 'html.parser')
        artist_list_html = soup.find_all(class_ = 'artist-list')

        # iterate over each track and assign values to music_dict
        for artist in artist_list_html:
            # get list of artists involved in current track
            artists = artist.find_all('li')
            current_artist_list = [artist.get_text() for artist in artists]

            # get name of current track
            track_name = artist.find_next_sibling('h2').get_text()
            track_name = track_name.replace('“', '')
            track_name = track_name.replace('”', '')

            # iterate over artists in the list of artists who made the track
            # if artist is already in music_dict, append to the list at
            # music_dict[artist_name]
            for artist_name in current_artist_list:
                if artist_name in music_dict:
                    music_dict[artist_name].append(track_name)
                else:
                    music_dict[artist_name] = [track_name]

    return music_dict

def write_new_tracks_json(new_tracks):
    """
    Write new_tracks dictionary into a local json file

    :param new_tracks: (dictionary) maps music artists to their music
    """
    # create json file of newly released track dictionary
    with open('new_tracks.json', 'w') as new_tracks_json:
        json.dump(new_tracks, new_tracks_json)

def get_tweet_volume(artist):
    """
    Uses Twitter API to get Twitter Volume statistic on a specified
    music artist.

    :param artist: (string) artist we are getting twitter volume for
    :return: (int) twitter volume statistic
    """

    # awaiting implementation


def main():
    # create dictionary of newly released tracks
    new_tracks = get_new_tracks()

    # write newly released tracks into json file
    write_new_tracks_json(new_tracks)



if __name__ == '__main__':
    main()
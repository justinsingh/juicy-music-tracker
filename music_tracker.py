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

def get_new_albums():
    """
    Scrapes Pitchfork for newly released albums and returns a dictionary
    of those albums and the artists who made them.

    :return: (dictionary) key = album name (string),
            value = list of dicts mapping "artists" string to list of
            artists who made the album
    """
    new_albums = {}

    for i in range(1, 4):
        # web page we are using to find newly released albums
        new_albums_page = requests.get(BASE_URL + "/reviews/albums/?page=" +
                                       str(i))

        soup = BeautifulSoup(new_albums_page.text, 'html.parser')

        review_list_html = soup.find_all(class_ = 'review')

        for review in review_list_html:
            #decompose genre and review author meta info from review html
            extra_info = review.find(class_ = 'review__meta')
            extra_info.decompose()

            # get list of artists involved in current album
            artists = review.find_all('li')
            current_artist_list = [artist.get_text() for artist in artists]

            # get name of current album
            album_name = review.find('h2').get_text()

            # update new_albums dict for key = album_name,
            # and value = list of dicts, the first being
            # a mapping of "artists" to current_artist_list
            new_albums[album_name] = [{"artists": current_artist_list}]

    return new_albums

def get_new_tracks():
    """
    Scrapes Pitchfork for newly released tracks and returns a dictionary
    of those tracks and the artists who made them.

    :return: (dictionary) key = music artist (string), value = newly released
            track(s) (list of strings)
    """
    # music dictionary that maps artist names to new music titles
    new_tracks = {}

    for i in range(1, 4):
        # web page we are using to find newly released tracks
        new_music_page = requests.get(BASE_URL + "/reviews/tracks/?page=" +
                                      str(i))

        # create BeautifulSoup object corresponding to new_music_page
        soup = BeautifulSoup(new_music_page.text, 'html.parser')

        # get html holding the artist name(s) and corresponding track
        artist_list_html = soup.find_all(class_ = 'artist-list')

        # iterate over each track and assign values to new_tracks
        for artist in artist_list_html:
            # get list of artists involved in current track
            artists = artist.find_all('li')
            current_artist_list = [artist.get_text() for artist in artists]

            # get name of current track
            track_name = artist.find_next_sibling('h2').get_text()
            track_name = track_name.replace('“', '')
            track_name = track_name.replace('”', '')

            # iterate over artists in the list of artists who made the track
            # if artist is already in new_tracks, append to the list at
            # new_tracks[artist_name]
            for artist_name in current_artist_list:
                if artist_name in new_tracks:
                    new_tracks[artist_name].append(track_name)
                else:
                    new_tracks[artist_name] = [track_name]

    return new_tracks

def write_json(data, file_name):
    """
    Writes a json file containing content of given data
    :param data: (dictionary) dictionary containing scraped web data
    :param file_name: (string) file name we are using for the json file
    """
    # create json file of given data
    with open(file_name + '.json', 'w') as music_data_file:
        json.dump(data, music_data_file)

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

    # create dictionary of newly released albums
    new_albums = get_new_albums()

    # write new_tracks into a json file
    write_json(new_tracks, 'new_tracks')

    #write new_albums into a json file
    write_json(new_albums, 'new_albums')

if __name__ == '__main__':
    main()
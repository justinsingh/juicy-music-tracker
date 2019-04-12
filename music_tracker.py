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
import string
import csv
from bs4 import BeautifulSoup
import requests

# global variables
BASE_URL = "https://pitchfork.com"

def get_new_music():
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
        track_title_html = soup.find_all(class_ = 'track-collection-item__title')

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

def main():
    # setup csv file with top row headings: Music Artist, Twitter Volume
    file = csv.writer(open('music_trends.csv', 'w'))
    file.writerow(["Music Artist", "Recent Tracks", "Twitter Volume"])

    new_music = get_new_music()

    for artist in new_music:
        file.writerow([artist, ', '.join(new_music[artist]), "N/A"])

if __name__ == '__main__':
    main()
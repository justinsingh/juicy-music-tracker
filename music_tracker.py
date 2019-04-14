# ----------------------------------------------------------------------

# Program:     Trending Music Tracker
# Purpose:     Use a web scraper on the Pitchfork website to get
#              the names of music artists releasing new music.
#              Assess their popularity on Spotify and Twitter using the
#              Spotify and Twitter API.
#
# Author:       Justin Singh
#
# ----------------------------------------------------------------------
"""
Implements a web scraper for the website https://pitchfork.com and
gets data on new music tracks and albums. Measures current Spotify and
Twitter popularity of albums and tracks using Spotify and Twitter APIs.
"""
import base64
import json
from bs4 import BeautifulSoup
import requests

# extract dictionary of API credentials from credentials.json
with open('credentials.json') as credentials_json:
    credentials = json.load(credentials_json)
    spotify_credentials = credentials["spotify_credentials"]

# global variables
BASE_PITCHFORK_URL = "https://pitchfork.com"
BASE_SPOTIFY_URL = "https://api.spotify.com/v1"
SPOTIFY_CLIENT_ID = spotify_credentials["CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = spotify_credentials["CLIENT_SECRET"]

def get_spotify_access_token(spotify_client_id, spotify_client_secret):
    """
    Make POST request to Spotify Accounts service to receive an access
    token required to make GET requests to the Spotify API.

    :param client_id: (string) client ID of Spotify developer app
    :param client_secret: (string) client secret of Spotify developer
                          app
    :return: (json text) json response from the POST request including
             the access token we are looking for
    """

    auth_str = spotify_client_id + ':' + spotify_client_secret
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    spotify_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + b64_auth_str
    }

    spotify_data = {
        'grant_type': 'client_credentials'
    }

    post_request = requests.post(url =
                                 'https://accounts.spotify.com/api/token',
                                 data = spotify_data,
                                 headers = spotify_headers)

    response_data = json.loads(post_request.text)
    return response_data



def search_spotify_item(query_keywords, item_type):
    """
    Use Spotify API to search for an item (track, album, or artist)

    :param query_keywords: (string) keywords of item we are trying to
                           search
    :param item_type: (string) item type we are searching for
    :return: (json text) information on item we searched for
    """
    spotify_access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID,
                                                    SPOTIFY_CLIENT_SECRET)
    spotify_headers = {
        'Authorization': 'Bearer ' + spotify_access_token['access_token']
    }

    query_url = BASE_SPOTIFY_URL + '/search?q=' + query_keywords.replace(' ',
                                    '%20') + '&type=' + item_type + '&limit=1'

    return requests.get(url = query_url, headers = spotify_headers).text

def get_spotify_item_id(item_json_str):
    """
    Extract the item ID of a Spotify item json text

    :param item_json_str: (json text) a returned json text from the
                          function search_spotify_item
    :return: (string) the item ID of a searched Spotify item
    """
    album_id_index = item_json_str.find('spotify:album:')
    album_id = item_json_str[album_id_index + 14:album_id_index + 36]
    return album_id

def get_spotify_album(item_id):
    """
    Get the complete json text data of an Album object from the Spotify
    API.

    :param item_id: (string) the Spotify ID for the album being searched
    :return: (json text) the json text data of an album on Spotify
    """
    spotify_access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID,
                                                    SPOTIFY_CLIENT_SECRET)

    spotify_headers = {
        'Authorization': 'Bearer ' + spotify_access_token['access_token']
    }
    query_url = BASE_SPOTIFY_URL + '/albums/' + item_id

    return requests.get(url = query_url, headers = spotify_headers).text

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
        new_albums_page = requests.get(BASE_PITCHFORK_URL +
                                       "/reviews/albums/?page=" +
                                       str(i))

        soup = BeautifulSoup(new_albums_page.text, 'html.parser')

        review_list_html = soup.find_all(class_ = 'review')

        for review in review_list_html:
            #decompose meta info from review html
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

    :return: (dictionary) key = music artist (string), value = newly
             released track(s) (list of strings)
    """
    # music dictionary that maps artist names to new music titles
    new_tracks = {}

    for i in range(1, 4):
        # web page we are using to find newly released tracks
        new_music_page = requests.get(BASE_PITCHFORK_URL +
                                      "/reviews/tracks/?page=" +
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

            new_tracks[track_name] = [{"artists": current_artist_list}]

    return new_tracks

def write_json(data, file_name):
    """
    Writes a json file containing content of given data
    :param data: (dictionary) dictionary containing scraped web data
    :param file_name: (string) file name we are using for the json file
    """
    # create json file of given data
    with open(file_name + '.json', 'w') as music_data_file:
        json.dump(data, music_data_file, indent = 2)

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
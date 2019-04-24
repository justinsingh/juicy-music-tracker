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
    :return: (string) json response from the POST request including
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
    :return: (string) json formatted information on item we searched for
    """
    spotify_access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID,
                                                    SPOTIFY_CLIENT_SECRET)
    spotify_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + spotify_access_token['access_token']
    }

    query_url = BASE_SPOTIFY_URL + '/search?q=' + query_keywords.replace(' ',
                                    '%20') + '&type=' + item_type + '&limit=1'

    return requests.get(url = query_url, headers = spotify_headers).text

def get_spotify_item_id(item_json_str):
    """
    Extract the item ID of a Spotify item json text

    :param item_json_str: (string) returned json formatted info from the
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
    :return: (string) json formatted info of an album on Spotify
    """
    spotify_access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID,
                                                    SPOTIFY_CLIENT_SECRET)

    spotify_headers = {
        'Authorization': 'Bearer ' + spotify_access_token['access_token']
    }
    query_url = BASE_SPOTIFY_URL + '/albums/' + item_id

    return requests.get(url = query_url, headers = spotify_headers).text

def get_many_spotify_albums(item_id_list):
    """
    Get complete json text data from a maximum of 20 albums specified
    by a list of item ID's.

    :param item_id_list: (list of strings) item ID of albums
    :return: (string) json formatted data of each album specified
             in item_id_list
    """
    spotify_access_token = get_spotify_access_token(SPOTIFY_CLIENT_ID,
                                                    SPOTIFY_CLIENT_SECRET)

    spotify_headers = {
        'Authorization': 'Bearer ' + spotify_access_token['access_token']
    }

    item_id_list_string = ''

    for id in item_id_list:
        item_id_list_string += id + ','

    query_url = BASE_SPOTIFY_URL + '/albums/?ids=' + \
                item_id_list_string.rstrip(',')

    return requests.get(url = query_url, headers = spotify_headers).text

def get_spotify_album_popularity(spotify_album):
    """
    Extracts the popularity field of a spotify album json text

    :param spotify_album: (string) the json formatted info of an album
    :return: (string) the number in string type of an album's popularity
    """
    album_popularity_index = spotify_album.find('\"popularity\" :')
    album_popularity = spotify_album[
                       album_popularity_index+15:album_popularity_index+17]
    album_popularity = album_popularity.replace(',', '')
    return album_popularity

def get_spotify_album_image(spotify_album):
    """
    Extracts the URL of a 640 pixel width x 300 pixel height album art
    image.

    :param spotify_album: (string) the json formatted info of an album
    :return: (string) the URL of the spotify_album's cover art image
    """
    album_image_index = spotify_album.find('\"height\" : 640')
    album_image_url = spotify_album[album_image_index+29:album_image_index+93]
    return album_image_url

def get_spotify_url(spotify_album):
    """
    Extracts the URL of the album's page on Spotify.

    :param spotify_album: (string) the json formatted info of an album
    :return: (string) the URL of the given album's Spotify page
    """
    album_url_index = spotify_album.find('https://open.spotify.com/album/')
    album_url = spotify_album[album_url_index:album_url_index+53]
    return album_url

def get_new_albums():
    """
    Scrapes Pitchfork for newly released albums and returns a dictionary
    of those albums and the artists who made them.

    :return: (dictionary) key = album name (string),
            value = list of dicts mapping "artists" string to list of
            artists who made the album
    """
    new_albums = {}

    for i in range(1, 6):
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

    for i in range(1, 6):
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
    with open('data/' + file_name + '.json', 'w') as music_data_file:
        json.dump(data, music_data_file, indent = 2)

def add_spotify_id(new_music_dict):
    """
    Search through the keys of a music dictionary and add a Spotify API
    'spotify_id' key for each entry of music.

    :param new_music_dict: (dict) dictionary of music albums (tracks not
                           yet implemented!)
    """
    for album in list(new_music_dict):
        album_id = get_spotify_item_id(search_spotify_item(album + " " +
                                            new_music_dict[album][
                                                0]["artists"][0], "album"))

        new_music_dict[album][0]['spotify_id'] = album_id

def add_popularity(new_music_dict):
    """
    Search through the keys of a music dictionary and add a Spotify API
    'popularity' key for each entry of music.

    :param new_music_dict: (dict) dictionary of music albums (tracks not
                           yet implemented!)
    """
    for album in list(new_music_dict):
            # assumes add_popularity has been called with current dict
            album_id = new_music_dict[album][0]['spotify_id']

            if '{' not in album_id:
                album_json = get_spotify_album(album_id)
                album_popularity = get_spotify_album_popularity(album_json)
                new_albums_value = new_music_dict[album][0]
                new_albums_value['popularity'] = album_popularity
            else:
                del new_music_dict[album]

def add_album_image(new_music_dict):
    """
    Search through the keys of a music dictionary and add a Spotify API
    'album_image_url' key for each entry of music.

    :param new_music_dict: (dict) dictionary of music albums (tracks not
                           yet implemented!)
    """
    for album in list(new_music_dict):
        # assumes add_popularity has been called with current dict
        album_id = new_music_dict[album][0]['spotify_id']

        album_json = get_spotify_album(album_id)
        album_image_url = get_spotify_album_image(album_json)
        if '{' not in album_image_url:
            new_albums_value = new_music_dict[album][0]
            new_albums_value['album_art_url'] = album_image_url
        else:
            del new_music_dict[album]

def add_spotify_url(new_music_dict):
    """
    Search through the keys of a music dictionary and add a Spotify API
    'spotify_url' key for each entry of music.

    :param new_music_dict: (dict) dictionary of music albums (tracks not
                           yet implemented!)
    """
    for album in list(new_music_dict):
        # assumes add_popularity has been called with current dict
        album_id = new_music_dict[album][0]['spotify_id']

        album_json = get_spotify_album(album_id)
        spotify_url = get_spotify_url(album_json)
        if '{' not in spotify_url:
            new_albums_value = new_music_dict[album][0]
            new_albums_value['spotify_url'] = spotify_url
        else:
            del new_music_dict[album]

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
    #new_tracks = get_new_tracks()

    # create dictionary of newly released albums
    new_albums = get_new_albums()

    # add spotify_id field to new_albums
    add_spotify_id(new_albums)

    # add popularity field to new_albums
    add_popularity(new_albums)

    # add album_art_url field to new_albums
    add_album_image(new_albums)

    # add spotify_url field to new_albums
    add_spotify_url(new_albums)

    # write new_tracks into a json file
    #write_json(new_tracks, 'new_tracks')

    #write new_albums into a json file
    write_json(new_albums, 'new_albums')

if __name__ == '__main__':
    main()
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, jsonify, render_template
import json
import time
import pandas as pd

# App config
app = Flask(__name__)

app.secret_key = 'SOMETHING-RANDOM'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
TOKEN_INFO = "token_info"

def login_checker():
    if not session.get(TOKEN_INFO) is None:
        return 'logged'
    else:
        return None

def range_input():
    time_frame = 'medium_term'
    ranges = request.form.get('submit_button')
    if ranges == "Last Month":
        time_frame = 'short_term'
    if ranges == "Last 6 Months":
        time_frame = 'medium_term'
    if ranges == 'All Time':
        time_frame = 'long_term'
    return time_frame
#Use user input to decide timeframe of data being pulled
def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="f1c4e68ebf9b4bf290c42542c3e72274",
            client_secret="5fb1d17706bd43378dc33088757552a2",
            redirect_uri=url_for("redirectPage", _external=True),
            scope="user-top-read playlist-modify-public", show_dialog=True)

def get_token():
    sp_oauth = create_spotify_oauth()
    token_info = session.get(TOKEN_INFO, None)
    if sp_oauth.is_token_expired(token_info):
        print('the token is expired')
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info
#Check if access token is valid, generate new one if it is expired

def auth_check():
    authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/home')
#Check if user is authorized through access token 

def get_album_cover(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.track(id)
    album_cover = data['album']['images'][1]['url']
    return album_cover
#Fetch single cover art of song or artist

def get_track_title(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.track(id)
    track_title = data['name']
    return track_title
#Fetch single track ID

def group_data(artist_ids, function):
    datas = []
    for i in range(len(artist_ids)):
        data = function(artist_ids[i])
        datas.append(data)
    return datas
#Generate full list of music data, such as all cover arts or IDs 

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)
#Send user to Spotify login

@app.route('/redirect')
def redirectPage():
    session.clear()
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect("/home")
#Start a new session, fetch access token and store it for later use, send user to home page

@app.route('/home')
def home():
    check = login_checker()
    return render_template('home.html', check=check)
#Home page

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/home')
#Logout page ends session

@app.route('/getTracks', methods = ["POST", "GET"])
def get_all_tracks():
    auth_check()
    time_frame = 'medium_term'
    #Default time frame for when user loads page
    if request.method == 'POST':
        time_frame = range_input()
        #If the request method is POST, the user was already on the page and selected a new time frame, so the program checks for the new time frame

    sp = spotipy.Spotify(auth=get_token()['access_token'])
    tracks = sp.current_user_top_tracks(limit=25, offset=0, time_range=time_frame)['items']
    #Fetch user's top 25 tracks
    track_ids = []
    for track in tracks:
        track_ids.append(track['id'])
        #Create a list for all track IDs

    def get_data(id):
        data = sp.track(id)
        album_title = data['album']['name']
        artists = 'By '
        i = 0
        for artist in (data['artists']):
            i += 1
            if i == (len(data['artists'])):
                artists += (artist['name'])
            else: 
                 artists += (artist['name']) + ', '
        track_data = [album_title, artists]
        return track_data
        #Create a list for all tracks' album titles and their artists 

    def to_dataframe(track_ids):
        all_tracks = []
        for i in range(len(track_ids)):
            track = get_data(track_ids[i])
            all_tracks.append(track)
        data_frame = pd.DataFrame(all_tracks)    
        return data_frame
        #Create a Pandas dataframe with track titles and their artists
        
    def get_url(id):
        data = sp.track(id)
        url = data['external_urls']['spotify']
        return url
        #Fetch singular track link
        
    def get_track_title(id):
        data = sp.track(id)
        track_title = data['name']
        return track_title
        #Fetch singular track title
        
    data_frame = to_dataframe(track_ids)
    album_covers = group_data(track_ids, get_album_cover)
    urls = group_data(track_ids, get_url)
    track_titles = group_data(track_ids, get_track_title)
    #Put all important data in lists
    check = login_checker()
    #Ensure user is logged in
    return render_template('getTracks.html', column_names=data_frame.columns.values, row_data=list(data_frame.values.tolist()), album_covers=album_covers, urls=urls, track_titles=track_titles, check=check, zip=zip)

    create_spotify_oauth()
    get_token()
    
#----------------------------Functions related to Top Artists----------------------------|
def get_name(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.artist(id)
    name = data['name']
    return name
    #Fetch singular artist name

def get_artist_cover(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.artist(id)
    artist_cover = data['images'][1]['url']
    return artist_cover 
    #Fetch singular artist picture
    
@app.route('/getArtists', methods = ["POST", "GET"])
def get_all_artists():
    auth_check()
    time_frame = 'medium_term'
    if request.method == 'POST':
        time_frame = range_input()
        #If the request method is POST, the user was already on the page and selected a new time frame, so the program checks for the new time frame

    sp = spotipy.Spotify(auth=get_token()['access_token'])
    artists = sp.current_user_top_artists(limit=25, offset=0, time_range=time_frame)['items']
    #Fetch user's top 25 artists
    artist_ids = []
    for artist in artists:
        artist_ids.append(artist['id'])
        #Generates list of all artist IDs

    def get_url(id):
        data = sp.artist(id)
        url = data['external_urls']['spotify']
        return url
        #Fetches singular artist URL

    artist_covers = group_data(artist_ids, get_artist_cover)
    urls = group_data(artist_ids, get_url)
    names = group_data(artist_ids, get_name)
    #Put all important data in lists
    check = login_checker()
    #Ensure user is logged in
    
    return render_template('getArtists.html', artist_covers=artist_covers, urls=urls, names=names, check=check)

    create_spotify_oauth()
    get_token()

@app.route('/seeds', methods = ["POST", "GET"])
def seed_type_selection():
    auth_check()

    if request.method == 'GET':
        return render_template('seedSelection.html')
    #If method is GET, then user has just gotten to the playlist creator, where they choose whether they base the playlist off of artists, genres, or tracks
    if request.method == 'POST':
        sp = spotipy.Spotify(auth=get_token()['access_token'])
        seeds = []
        ranges = request.form.get('seed_button')
        seed_type = ''
        #If method is GET, then user has selected a type of seed (artists, genres, tracks), which is now considered
        if ranges == "Top Artists":
            seed_type = 'artists'
            artists = sp.current_user_top_artists(limit=10, offset=0, time_range='short_term')['items']
            for artist in artists:
                seeds.append(artist['id'])  

            names = group_data(seeds, get_name)
            artist_covers = group_data(seeds, get_artist_cover)
            return render_template('makePlaylist.html', seed_type=seed_type, artist_covers=artist_covers, seeds=seeds, names=names, zip=zip)
            #If user chooses to base playlist on artists, 10 options are given

        if ranges == "Top Tracks":
            seed_type = 'tracks'
            tracks = sp.current_user_top_tracks(limit=10, offset=0, time_range='short_term')['items']
            for track in tracks:
                seeds.append(track['id'])

            def get_artist(id):
                data = sp.track(id)
                artists = 'By '
                i = 0
                for artist in (data['artists']):
                    i += 1
                    if i == (len(data['artists'])):
                        artists += (artist['name'])
                    else: 
                         artists += (artist['name']) + ', '
                return artists

            def group_artists(seeds):
                artists = []
                for i in range(len(seeds)):
                    artist = get_artist(seeds[i])
                    artists.append(artist)
                return artists

            artists = group_data(seeds, get_artist)
            track_titles = group_data(seeds, get_track_title)
            album_covers = group_data(seeds, get_album_cover)
            return render_template('makePlaylist.html', seed_type=seed_type, track_titles=track_titles, artists=artists, seeds=seeds, album_covers=album_covers, zip=zip)
            #If user chooses to base playlist on tracks, 10 options are given
            
        if ranges == "Top Genres":
            seed_type = 'genres'
            genre_list = []
            artists = sp.current_user_top_artists(limit=10, offset=0, time_range='short_term')['items']
            for genres in artists:
                for i in genres['genres']:
                    i = i.replace(" ", "-")
                    genre_list.append(i)
                    #Add each genre to the list, and format it so it can be displayed properly
            seeds = list(dict.fromkeys(genre_list))
            return render_template('makePlaylist.html', seed_type=seed_type, seeds=seeds, zip=zip)   
            #If user chooses to base playlist on tracks, options are given

    create_spotify_oauth()
    get_token()

@app.route('/displayPlaylist', methods = ["POST", "GET"])
def display_playlist():
    auth_check()
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    new_tracks = []

    def get_track_ids(new_tracks):
        track_ids = []
        for track in new_tracks:
            track_ids.append(track['id'])
        return track_ids

    if request.form.get('types') == 'genre':
        picked_genres = request.form.getlist('tracks')
        new_tracks = sp.recommendations(seed_genres=picked_genres, max_popularity=60)['tracks']
        print('genre')
        new_tracks = get_track_ids(new_tracks)
    if request.form.get('types') == 'track':
        ids = request.form.getlist('tracks')
        print('track')
        new_tracks = sp.recommendations(seed_tracks=ids, max_popularity=60)['tracks']
        new_tracks = get_track_ids(new_tracks)
    if request.form.get('types') == 'artist':
        ids = request.form.getlist('tracks')
        new_tracks = sp.recommendations(seed_artists=ids, max_popularity=60)['tracks']
        print('artist')
        new_tracks = get_track_ids(new_tracks)
    #New Tracks are fetched depending on which seed (tracks, artists, genres)

    playlist_title = request.form.get('playlist-title')
    user_id = sp.me()['id']
    playlist_id = sp.user_playlist_create(user=user_id, name=playlist_title, public=True, description='')['id']
    playlist_url = "https://open.spotify.com/embed/playlist/" + playlist_id
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=new_tracks, position=None)
    return render_template('viewPlaylist.html', playlist_url=playlist_url)

    #Playlist is created and put on display for the user. It can also be found in their library

    create_spotify_oauth()
    get_token()

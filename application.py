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

def auth_check():
    authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/home')

def get_album_cover(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.track(id)
    album_cover = data['album']['images'][1]['url']
    return album_cover

def get_track_title(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.track(id)
    track_title = data['name']
    return track_title

def group_data(artist_ids, function):
    datas = []
    for i in range(len(artist_ids)):
        data = function(artist_ids[i])
        datas.append(data)
    return datas

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    session.clear()
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect("/home")

@app.route('/home')
def home():
    check = login_checker()
    return render_template('home.html', check=check)

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/home')

@app.route('/getTracks', methods = ["POST", "GET"])
def get_all_tracks():
    auth_check()
    time_frame = 'medium_term'
    if request.method == 'POST':
        time_frame = range_input()

    sp = spotipy.Spotify(auth=get_token()['access_token'])
    tracks = sp.current_user_top_tracks(limit=25, offset=0, time_range=time_frame)['items']
    track_ids = []
    for track in tracks:
        track_ids.append(track['id'])

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

    def to_dataframe(track_ids):
        all_tracks = []
        for i in range(len(track_ids)):
            track = get_data(track_ids[i])
            all_tracks.append(track)
        data_frame = pd.DataFrame(all_tracks)    
        return data_frame

    def get_url(id):
        data = sp.track(id)
        url = data['external_urls']['spotify']
        return url

    def get_track_title(id):
        data = sp.track(id)
        track_title = data['name']
        return track_title

    data_frame = to_dataframe(track_ids)
    album_covers = group_data(track_ids, get_album_cover)
    urls = group_data(track_ids, get_url)
    track_titles = group_data(track_ids, get_track_title)
    check = login_checker()
    return render_template('getTracks.html', column_names=data_frame.columns.values, row_data=list(data_frame.values.tolist()), album_covers=album_covers, urls=urls, track_titles=track_titles, check=check, zip=zip)

    create_spotify_oauth()
    get_token()

def get_name(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.artist(id)
    name = data['name']
    return name

def get_artist_cover(id):
    sp = spotipy.Spotify(auth=get_token()['access_token'])
    data = sp.artist(id)
    artist_cover = data['images'][1]['url']
    return artist_cover 

@app.route('/getArtists', methods = ["POST", "GET"])
def get_all_artists():
    auth_check()
    time_frame = 'medium_term'
    if request.method == 'POST':
        time_frame = range_input()

    sp = spotipy.Spotify(auth=get_token()['access_token'])
    artists = sp.current_user_top_artists(limit=25, offset=0, time_range=time_frame)['items']
    artist_ids = []
    for artist in artists:
        artist_ids.append(artist['id'])

    def get_url(id):
        data = sp.artist(id)
        url = data['external_urls']['spotify']
        return url

    artist_covers = group_data(artist_ids, get_artist_cover)
    urls = group_data(artist_ids, get_url)
    names = group_data(artist_ids, get_name)
    check = login_checker()

    #return jsonify(names + artist_covers + urls)
    return render_template('getArtists.html', artist_covers=artist_covers, urls=urls, names=names, check=check)

    create_spotify_oauth()
    get_token()

@app.route('/seeds', methods = ["POST", "GET"])
def seed_type_selection():
    auth_check()

    if request.method == 'GET':
        return render_template('seedSelection.html')

    if request.method == 'POST':
        sp = spotipy.Spotify(auth=get_token()['access_token'])
        seeds = []
        ranges = request.form.get('seed_button')
        seed_type = ''

        if ranges == "Top Artists":
            seed_type = 'artists'
            artists = sp.current_user_top_artists(limit=10, offset=0, time_range='short_term')['items']
            for artist in artists:
                seeds.append(artist['id'])  

            names = group_data(seeds, get_name)
            artist_covers = group_data(seeds, get_artist_cover)
            return render_template('makePlaylist.html', seed_type=seed_type, artist_covers=artist_covers, seeds=seeds, names=names, zip=zip)

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
            
            
        if ranges == "Top Genres":
            seed_type = 'genres'
            genre_list = []
            artists = sp.current_user_top_artists(limit=10, offset=0, time_range='short_term')['items']
            for genres in artists:
                for i in genres['genres']:
                    i = i.replace(" ", "-")
                    genre_list.append(i)
            seeds = list(dict.fromkeys(genre_list))
            return render_template('makePlaylist.html', seed_type=seed_type, seeds=seeds, zip=zip)   


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

    playlist_title = request.form.get('playlist-title')
    user_id = sp.me()['id']
    playlist_id = sp.user_playlist_create(user=user_id, name=playlist_title, public=True, description='')['id']
    playlist_url = "https://open.spotify.com/embed/playlist/" + playlist_id
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=new_tracks, position=None)
    return render_template('viewPlaylist.html', playlist_url=playlist_url)
    #return sp.playlist(playlist_id=playlist_id)

    create_spotify_oauth()
    get_token()
import streamlit as st
from functions import artist_info
from functions import unique_playlists
from functions import get_predictions
from functions import get_tracks
import random
import config
import spotipy
import spotipy.util as util
import surprise
from surprise import SVD
import pickle


st.markdown("<h1 style='text-align: center; color: rgb(29,185,84); font: Proxima Nova; font-size: 75px;''>Welcome to <i>playlist.append()</i></h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: black; font: Proxima Nova; font-size: 25px;''>Create your own Spotify playlist in just two steps</i></h1>", unsafe_allow_html=True)
# st.title('Welcome to playlist.append()!')
st.write('')
st.write('')
st.write('')
st.write('')
# artist_list = st.multiselect("Pick 1-5 artists", sorted(list(artist_info.keys()), key=str.lower))
artist_list = st.multiselect('Enter up to 5 artists:', sorted(['Drake', 'Kendrick Lamar', 'J. Cole', 'Kanye West', 'Lil Wayne', 'Eminem'], key=str.lower))
st.write('')
if len(artist_list) > 5:
    st.write("I'm sorry, you can only pick 5 artists at most.")
    st.write('')
username = st.text_input('Enter your name:')
st.write('')
st.write('')
st.write('')
st.write('')


if (len(artist_list) > 0) and (username != ''):

    predicted_playlists = []
    for artist_name in artist_list:
        if len(artist_list) == 1:
            predictions = get_predictions(artist_info[artist_name][0], unique_playlists[artist_info[artist_name][1]], 50)
            preds = random.choices(predictions, k=10)
        elif len(artist_list) == 2:
            predictions = get_predictions(artist_info[artist_name][0], unique_playlists[artist_info[artist_name][1]], 50)
            preds = random.choices(predictions, k=10)
        elif len(artist_list) == 3:
            predictions = get_predictions(artist_info[artist_name][0], unique_playlists[artist_info[artist_name][1]], 25)
            preds = random.choices(predictions, k=5)
        elif len(artist_list) == 4:
            predictions = get_predictions(artist_info[artist_name][0], unique_playlists[artist_info[artist_name][1]], 25)
            preds = random.choices(predictions, k=5)
        elif len(artist_list) == 5:
            predictions = get_predictions(artist_info[artist_name][0], unique_playlists[artist_info[artist_name][1]], 30)
            preds = random.choices(predictions, k=6)
        for item in preds:
            if item[0] not in predicted_playlists:
                predicted_playlists.append(item[0])



    all_tracks = []
    for playlistID in predicted_playlists:
        tracks = get_tracks(playlistID)
        if (len(artist_list) == 1) or (len(artist_list) == 2):
            selection = random.choices(tracks, k=7)
        elif (len(artist_list) == 3) or (len(artist_list) == 4):
            selection = random.choices(tracks, k=5)
        elif len(artist_list) == 5:
            selection = random.choices(tracks, k=3)
        for song in selection:
            if song not in all_tracks:
                all_tracks.append(song)
    random.shuffle(all_tracks)


    scope = 'playlist-modify-public'
    redirect_uri = 'http://www.google.com/'
    token = util.prompt_for_user_token(config.user,
                               scope,
                               client_id=config.client_id,
                               client_secret=config.client_secret,
                               redirect_uri=redirect_uri)

    if username[-1] == 's':
        playlist_name = username + "' Mix"
    else:
        playlist_name = username + "'s Mix"

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        new_playlist = sp.user_playlist_create(config.user, playlist_name, description='Strictly bangers, brought to you by playlist.append()')
        results = sp.user_playlist_add_tracks(config.user, new_playlist['id'], all_tracks[:50])
        st.write('Your playlist is ready, ' + username + '!')
        st.write('')
        st.write('Here is the link to your playlist:     ' + new_playlist['external_urls']['spotify'])
    else:
        st.write("Can't get token for", username)

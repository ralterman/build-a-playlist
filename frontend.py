import streamlit as st
from functions import artist_info
from functions import genre_dict
from functions import get_predictions
from functions import get_tracks
import random
import config
import spotipy
import spotipy.util as util
import surprise
from surprise import SVD
import pickle


# Make background black
st.markdown("<style>body {background-color: rgb(25, 20, 20);}</style>", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: rgb(30, 215, 96); font: Proxima Nova; font-size: 72px;''>Welcome to <i>playlist.append()</i></h1>", unsafe_allow_html=True)

# Subtitle
st.markdown("<h3 style='text-align: center; color: white; font: Proxima Nova; font-size: 25px;''>Create a unique Spotify playlist in just two easy steps</i></h3>", unsafe_allow_html=True)

# (Blank lines for spacing purposes)
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')

# Text box to enter artist names
st.markdown("<h6 style='text-align: left; color: white; font: Proxima Nova; font-size: 17px;''>Enter 1-5 artists (separated by commas):</h6>", unsafe_allow_html=True)
artists = st.text_input('')

# Split string of artists into a list and convert everything to lowercase
artist_l = artists.split(', ')
artist_list = [artist.lower() for artist in artist_l]

# Check if user entered more than the allotted 5 artists
if len(artist_list) > 5:
    st.markdown("<h6 style='text-align: left; color: rgb(246, 51, 102); font: Proxima Nova; font-size: 15px;''>I'm sorry, you can only pick 5 artists at most.</h6>", unsafe_allow_html=True)
    st.write('')

# Text box to enter user's name for playlist name
st.write('')
st.markdown("<h6 style='text-align: left; color: white; font: Proxima Nova; font-size: 17px;''>Type in your name below and hit enter</h6>", unsafe_allow_html=True)
username = st.text_input('', key='username')

# (Blank lines for spacing purposes)
st.write('')
st.write('')
st.write('')
st.write('')
st.write('')



# Allow rest of program to run only if at least one artist has been entered and the user's name
if len(artist_l) and (username != ''):


    # Get random selection of recommended playlists via SVD for each artist input, based on total number of artists entered
    predicted_playlists = []
    for artist_name in artist_list:
        if len(artist_list) == 1:
            predictions = get_predictions(artist_info[artist_name][0], genre_dict[artist_info[artist_name][1]], 50)
            preds = random.choices(predictions, k=10)
        elif len(artist_list) == 2:
            predictions = get_predictions(artist_info[artist_name][0], genre_dict[artist_info[artist_name][1]], 60)
            preds = random.choices(predictions, k=10)
        elif len(artist_list) == 3:
            predictions = get_predictions(artist_info[artist_name][0], genre_dict[artist_info[artist_name][1]], 55)
            preds = random.choices(predictions, k=5)
        elif len(artist_list) == 4:
            predictions = get_predictions(artist_info[artist_name][0], genre_dict[artist_info[artist_name][1]], 60)
            preds = random.choices(predictions, k=5)
        elif len(artist_list) == 5:
            predictions = get_predictions(artist_info[artist_name][0], genre_dict[artist_info[artist_name][1]], 65)
            preds = random.choices(predictions, k=5)
        for item in preds:
            if item[0] not in predicted_playlists:
                predicted_playlists.append(item[0])



    # Get all songs from each recommended playlist and choose random number of songs from each, based on number of artists entered
    all_tracks = []
    for playlistID in predicted_playlists:
        tracks = get_tracks(playlistID)
        if len(artist_list) == 1:
            selection = random.choices(tracks, k=7)
        elif len(artist_list) == 2:
            selection = random.choices(tracks, k=4)
        elif len(artist_list) == 3:
            selection = random.choices(tracks, k=5)
        elif len(artist_list) == 4:
            selection = random.choices(tracks, k=4)
        elif len(artist_list) == 5:
            selection = random.choices(tracks, k=3)
        for song in selection:
            if song not in all_tracks:
                all_tracks.append(song)
    # Shuffle the songs
    random.shuffle(all_tracks)



    # Authenticate user
    scope = 'playlist-modify-public'
    redirect_uri = 'http://www.google.com/'
    token = util.prompt_for_user_token(config.user,
                               scope,
                               client_id=config.client_id,
                               client_secret=config.client_secret,
                               redirect_uri=redirect_uri)


    # Make playlist name from inputted username, first adding 's
    if username[-1] == 's':
        playlist_name = username + "' Mix"
    else:
        playlist_name = username + "'s Mix"


    # Create new playlist with name and description, and add 50 tracks from recommended playlists
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        new_playlist = sp.user_playlist_create(config.user, playlist_name, description='Strictly bangers, brought to you by playlist.append()')
        results = sp.user_playlist_add_tracks(config.user, new_playlist['id'], all_tracks[:50])
        link = new_playlist['external_urls']['spotify']

        # Inform user that his/her playlist is ready
        st.markdown("<h6 style='text-align: left; color: white; font: Proxima Nova; font-size: 17px;''>Your playlist is ready, %s!</h1>"% username, unsafe_allow_html=True)
        st.write('')

        # Print link for access to playlist
        st.markdown("<h6 style='text-align: left; color: white; font: Proxima Nova; font-size: 17px;''>Here is the link to your playlist: <a href='{}' style='color:rgb(30, 215, 96); font-size: 16px;' ><b>{}</b></a>".format(link, link), unsafe_allow_html=True)


        # Create separate playlist of songs from everyone's individual playlists (for science fair purposes only)
        # sp.user_playlist_add_tracks(config.user, '12cQLzXvglwDdzC7jkgDzr', random.choices(all_tracks, k=2))

    else:
        st.write("Can't get token for " + username)

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

final_model = pickle.load(open('final_model3.pkl', 'rb'))


def main():
    pick = True
    artist_list = []
    while pick == True:
        print('')
        print('')
        artist = input('Pick an artist: ')
        while artist not in artist_info:
            artist = input("I'm sorry, I don't recognize that artist. Please pick a different artist: ")
        artist_list.append(artist)
        add = input('Would you like to pick another artist? [y/n]: ')
        if (add != 'y') and (add != 'n'):
            add = input("I'm sorry, I didn't quite get that. Would you like to pick another artist? [y/n]: ")
            print('')
        while (add == 'y') and (len(artist_list) < 5):
            print('')
            artist = input('Pick another artist: ')
            while artist not in artist_info:
                artist = input("I'm sorry, I don't recognize that artist. Please pick a different artist: ")
            artist_list.append(artist)
            if len(artist_list) < 5:
                add = input('Would you like to pick another artist? [y/n]: ')
                if (add != 'y') and (add != 'n'):
                    add = input("I'm sorry, I didn't quite get that. Would you like to pick another artist? [y/n]: ")
        print('')
        pick = False

    print('')
    username = input('Please enter your name: ')
    print('')
    print('')


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
        print('Your playlist is ready!')
        print('')
        print('Here is the link to your playlist: ' + new_playlist['external_urls']['spotify'])
        print('')
        print('')
    else:
        print("Can't get token for", username)
        print('')
        print('')



if __name__== "__main__":
    main()

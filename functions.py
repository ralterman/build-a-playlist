import config
import pickle
import surprise
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from surprise import dump



client_credentials_manager = SpotifyClientCredentials(client_id=config.client_id, client_secret=config.client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


artist_info = pickle.load(open('artist_info.pkl', 'rb'))
unique_playlists = pickle.load(open('playlist_ids2.pkl', 'rb'))
new_remastered = pickle.load(open('new_remastered.pkl', 'rb'))


final_model = pickle.load(open('final_model.pkl', 'rb'))

def get_predictions(artist, list_of_playlists, num_selections):
    rankings = []
    for playlist in list_of_playlists:
        prediction = final_model.predict(artist, playlist)
        if prediction.r_ui != None:
            rankings.append((prediction.iid, prediction.r_ui))
        else:
            rankings.append((prediction.iid, prediction.est))
    sorted_rankings = sorted(rankings, reverse=True, key=lambda x: x[1])[:num_selections]
    return sorted_rankings



def get_tracks(playlist_id):
    bad = ['Piano Arrangement', 'Piano Version', '(Cover)', '[Cover]']
    songs = []
    offset = 0
    count = 0
    tracks = sp.playlist_tracks(playlist_id, offset=offset)
    while count < tracks['total']:
        idx = 0
        try:
            while idx < len(tracks['items']):
                count += 1
                track_id = tracks['items'][idx]['track']['id']
                name = tracks['items'][idx]['track']['name']
                artists = tracks['items'][idx]['track']['artists']
                idx2 = 0
                if not any(word in name for word in bad):
                    while idx2 < len(artists):
                        if 'Piano' not in artists[idx2]['name']:
                            songs.append(track_id)
                        idx2 += 1
                idx += 1
            offset += 100
            tracks = sp.playlist_tracks(playlist_id, offset=offset)
        except:
            break
    return list(set(songs))

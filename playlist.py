import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from tqdm import tqdm
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import time
from sklearn.preprocessing import MinMaxScaler
from surprise import Dataset, Reader
from surprise import SVD
from surprise import accuracy
from surprise.model_selection import cross_validate, train_test_split
from surprise import NormalPredictor
from surprise.model_selection import GridSearchCV



client_credentials_manager = SpotifyClientCredentials(client_id=config.client_id, client_secret=config.client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Spotify genres
sp_genres = sp.recommendation_genre_seeds()['genres']
sp_genres

# Narrowed-down genre list
genres = ['Alternative/Indie', 'Blues', 'Classical', 'Country', 'EDM', 'Hip-Hop/Rap',
          'Jazz', 'K-Pop', 'Latin', 'Metal', 'Pop', 'R&B', 'Reggae', 'Rock']


# Get unique playlist IDs for each above genre (modified from getting repeats across different genres)
def get_playlists(genre_list):
    all_playlists = {}
    for genre in genre_list:
        playlist_ids = []
        offset = 0
        search = sp.search(q=genre, type='playlist', limit=50, offset=offset)
        while search:
            idx = 0
            try:
                while idx < len(search['playlists']['items']):
                    id = search['playlists']['items'][idx]['id']
                    if id not in playlist_ids:
                        if id not in [x for y in list(all_playlists.values()) for x in y]:
                            playlist_ids.append(id)
                    idx += 1
                offset += 50
                search = sp.search(q=genre, limit=50, offset=offset, type='playlist')
            except:
                break
        all_playlists[genre] = playlist_ids
    return all_playlists

# unique_playlists = get_playlists(tqdm(genres))
# pickle.dump(unique_playlists, open('playlist_ids2.pkl', 'wb'))


unique_playlists = pickle.load(open('playlist_ids2.pkl', 'rb'))

# Make sure they are all unique with modified get_playlists function
count = []
for g in unique_playlists:
    count.extend(unique_playlists[g])

print (len(count))
print (len(set(count)))


# Create bar chart of genres and playlist counts
genre_counts = {}
for g in unique_playlists:
    genre_counts[g] = len(unique_playlists[g])

plt.figure(figsize=(15,7))
sns.barplot(list(genre_counts.keys()), list(genre_counts.values()))
plt.xticks(rotation=45)



#------------------------------------------------------------------------------------------



# Get artist IDs for each playlist ID
def get_artists(playlist_id_dict):
    all_artists = []
    genre_number = 1
    for genre in playlist_id_dict:
        print (genre_number)
        art_by_gen = []
        for playlist_id in tqdm(playlist_id_dict[genre]):
            offset = 0
            count = 0
            try:
                artist = sp.playlist_tracks(playlist_id, offset=offset)
            except:
                continue
            while count < artist['total']:
                idx = 0
                try:
                    while idx < len(artist['items']):
                        count += 1
                        idx2 = 0
                        while idx2 < len(artist['items'][idx]['track']['artists']):
                            artist_id = artist['items'][idx]['track']['artists'][idx2]['id']
                            art_by_gen.append((playlist_id, artist_id))
                            idx2 += 1
                        idx += 1
                    offset += 100
                    artist = sp.playlist_tracks(playlist_id, offset=offset)
                except:
                    break
            time.sleep(.15)
        all_artists.append(art_by_gen)
        pickle.dump(all_artists, open('artist_tuples.pkl', 'wb'))
        genre_number += 1
    return all_artists

# artists_per_playlist = get_artists(playlists_per_genre)


artists_per_playlist = pickle.load(open('artist_tuples_list.pkl', 'rb'))
all = [item for sublist in artists_per_playlist for item in sublist]
len(all)


master_df = pd.DataFrame(all, columns=['playlist_ID', 'artist_ID'])

artists_counts = master_df.groupby('playlist_ID').count()
master_counts = pd.DataFrame({'count': master_df.groupby(['playlist_ID', 'artist_ID']).size()}).reset_index()

master = pd.merge(master_counts, artists_counts, how='right', on='playlist_ID')
master = master.rename(columns={'artist_ID_x': 'artist_ID', 'artist_ID_y': 'total'})

master['scaled'] = master['count'] / master['total']
master = master.dropna()


pickle.dump(master, open('master.pkl', 'wb'))



#------------------------------------------------------------------------------------------



master = pickle.load(open('master.pkl', 'rb'))


reader = Reader(rating_scale=(0, 1))
data = Dataset.load_from_df(master[['playlist_ID', 'artist_ID', 'scaled']], reader)
trainset, testset = train_test_split(data, test_size=.2)


svd = SVD()
svd.fit(trainset)
predictions = svd.test(testset)

accuracy.rmse(predictions)
accuracy.mae(predictions)


param_grid = {'n_factors': [50, 150], 'n_epochs': [10, 30], 'lr_all': [0.004, 0.006], 'reg_all': [0.01, 0.03]}
gs1 = GridSearchCV(SVD, param_grid=param_grid, joblib_verbose=100)
gs1.fit(data)

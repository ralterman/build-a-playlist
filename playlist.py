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
tqdm.pandas()



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
plt.title('Playlist Count by Search Term (Genre)', fontsize=24)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)



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

# artists_per_playlist = get_artists(unique_playlists)


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


master.scaled.hist()
plt.ylim(ymin=0, ymax=60000)

master.total.hist()


master = master[(master.total >= 20) & (master.total <= 500)]


bad_rows = master[master['scaled'] > .40].index.tolist()

bad_playlists = []
for i in bad_rows:
    bad_playlists.append(master.loc[i, 'playlist_ID'])

unique_bad_playlists = list(set(bad_playlists))


master['good_scale'] = master.playlist_ID.progress_apply(lambda x: 0 if x in unique_bad_playlists else 1)


remastered = master[master.good_scale == 1]

remastered.playlist_ID.nunique()
remastered.artist_ID.nunique()

cols = remastered.columns.tolist()
cols = ['artist_ID', 'playlist_ID', 'count', 'total', 'scaled', 'good_scale']
remastered = remastered[cols]


pickle.dump(remastered, open('remastered.pkl', 'wb'))



#------------------------------------------------------------------------------------------



remastered = pickle.load(open('remastered.pkl', 'rb'))

remastered.head()

occurences = pd.DataFrame(remastered['artist_ID'].value_counts()).reset_index()
occurences = occurences.rename(columns={'index':'artist_ID', 'artist_ID':'appearances'})

occurences.appearances.describe()

new_master = pd.merge(remastered, occurences, how='right', on='artist_ID')


bad_rows2 = new_master[new_master['appearances'] < 5].index.tolist()

bad_playlists2 = []
for i in bad_rows2:
    bad_playlists2.append(new_master.loc[i, 'playlist_ID'])

unique_bad_playlists2 = list(set(bad_playlists2))


new_master = new_master[new_master.appearances >= 5]

new_master['contains_nonpopular'] = new_master.playlist_ID.progress_apply(lambda x: 1 if x in unique_bad_playlists2 else 0)

new_remastered = new_master[new_master.contains_nonpopular == 0]


pickle.dump(new_remastered, open('new_remastered.pkl', 'wb'))



#------------------------------------------------------------------------------------------



new_remastered = pickle.load(open('new_remastered.pkl', 'rb'))

reader = Reader(rating_scale=(0, 1))
data = Dataset.load_from_df(master[['artist_ID', 'playlist_ID', 'scaled']], reader)
trainset, testset = train_test_split(data, test_size=.2)


svd = SVD()
svd.fit(trainset)
predictions = svd.test(testset)

accuracy.rmse(predictions)
accuracy.mae(predictions)


param_grid = {'n_factors': [50, 150], 'n_epochs': [10, 30], 'lr_all': [0.004, 0.006], 'reg_all': [0.01, 0.03]}
gs1 = GridSearchCV(SVD, param_grid=param_grid, cv=3, joblib_verbose=5)
gs1.fit(data)


gs1.best_score['rmse'])
gs1.best_params['rmse'])



#------------------------------------------------------------------------------------------



artists_per_playlist = pickle.load(open('artist_tuples_list.pkl', 'rb'))

all_artists = list(set([item[1] for sublist in artists_per_playlist for item in sublist]))


artist_dict = {}
for artist in tqdm(all_artists):
    try:
        name = sp.artist(artist)['name']
    except:
        continue
    artist_dict[name] = artist
    time.sleep(.2)


pickle.dump(artist_dict, open('artists.pkl', 'wb'))



def label_genre(row, genre_dict):
    if row['playlist_ID'] in genre_dict['Alternative/Indie']:
        return 'Alternative/Indie'
    elif row['playlist_ID'] in genre_dict['Blues']:
        return 'Blues'
    elif row['playlist_ID'] in genre_dict['Classical']:
        return 'Classical'
    elif row['playlist_ID'] in genre_dict['Country']:
        return 'Country'
    elif row['playlist_ID'] in genre_dict['EDM']:
        return 'EDM'
    elif row['playlist_ID'] in genre_dict['Hip-Hop/Rap']:
        return 'Hip-Hop/Rap'
    elif row['playlist_ID'] in genre_dict['Jazz']:
        return 'Jazz'
    elif row['playlist_ID'] in genre_dict['K-Pop']:
        return 'K-Pop'
    elif row['playlist_ID'] in genre_dict['Latin']:
        return 'Latin'
    elif row['playlist_ID'] in genre_dict['Metal']:
        return 'Metal'
    elif row['playlist_ID'] in genre_dict['Pop']:
        return 'Pop'
    elif row['playlist_ID'] in genre_dict['R&B']:
        return 'R&B'
    elif row['playlist_ID'] in genre_dict['Reggae']:
        return 'Reggae'
    elif row['playlist_ID'] in genre_dict['Rock']:
        return 'Rock'

new_remastered['genre'] = new_remastered.apply(lambda row: label_genre(row, unique_playlists), axis=1)


# {'name': (artist_id, [list of genres of the playlists that artist is in])}

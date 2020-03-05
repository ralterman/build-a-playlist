import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pandas as pd
from collections import Counter
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
from surprise import dump
import random
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

non_unique_playlists = pickle.load(open('playlist_ids.pkl', 'rb'))

unique_playlists = pickle.load(open('playlist_ids2.pkl', 'rb'))

# Make sure they are all unique with modified get_playlists function
count = []
for g in non_unique_playlists:
    count.extend(non_unique_playlists[g])

print (len(count))
print (len(set(count)))


# Create bar chart of genres and playlist counts
genre_counts = {}
for g in non_unique_playlists:
    genre_counts[g] = len(non_unique_playlists[g])

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


master.scaled.hist(bins=20)
plt.ylim(ymin=0, ymax=100000)
plt.xlim(xmin=0, xmax=.50)

master.total.hist(bins=2000)
plt.ylim(ymin=0, ymax=300000)
plt.xlim(xmin=0, xmax=600)


master = master[(master.total >= 20) & (master.total <= 500)]
master.playlist_ID.nunique()

bad_rows = master[master['scaled'] > .20].index.tolist()

bad_playlists = []
for i in bad_rows:
    bad_playlists.append(master.loc[i, 'playlist_ID'])

unique_bad_playlists = list(set(bad_playlists))


remastered = master[master.scaled <= .20]

remastered['good_scale'] = remastered.playlist_ID.progress_apply(lambda x: 0 if x in unique_bad_playlists else 1)


remastered = remastered[remastered.good_scale == 1]

remastered.playlist_ID.nunique()
remastered.artist_ID.nunique()

cols = remastered.columns.tolist()
cols = ['artist_ID', 'playlist_ID', 'count', 'total', 'scaled', 'good_scale']
remastered = remastered[cols]


pickle.dump(remastered, open('remastered.pkl', 'wb'))



#------------------------------------------------------------------------------------------



remastered = pickle.load(open('remastered.pkl', 'rb'))


occurences = pd.DataFrame(remastered['artist_ID'].value_counts()).reset_index()
occurences = occurences.rename(columns={'index':'artist_ID', 'artist_ID':'appearances'})

occurences.appearances.describe()

occurences.appearances.hist(bins=1000)
plt.ylim(ymin=0, ymax=6000)
plt.xlim(xmin=10, xmax=30)

new_master = pd.merge(remastered, occurences, how='right', on='artist_ID')


bad_rows2 = new_master[new_master['appearances'] < 12].index.tolist()

bad_playlists2 = []
for i in bad_rows2:
    bad_playlists2.append(new_master.loc[i, 'playlist_ID'])

unique_bad_playlists2 = list(set(bad_playlists2))


new_master = new_master[new_master.appearances >= 12]

new_master['contains_nonpopular'] = new_master.playlist_ID.progress_apply(lambda x: 1 if x in unique_bad_playlists2 else 0)

new_remastered = new_master[new_master.contains_nonpopular == 0]

new_remastered.shape
new_remastered.playlist_ID.nunique()
new_remastered.artist_ID.nunique()


pickle.dump(new_remastered, open('new_remastered2.pkl', 'wb'))

new_remastered

unique = pd.DataFrame(new_remastered.groupby('playlist_ID'))

playlist_list = unique[0].tolist()

len(playlist_list)



genre_dict = {}
for genre in unique_playlists:
    g_list = []
    for p in unique_playlists[genre]:
        if p in playlist_list:
            g_list.append(p)
    genre_dict[genre] = g_list

pickle.dump(genre_dict, open('genre_dict.pkl', 'wb'))

genre_dict = pickle.load(open('genre_dict.pkl', 'rb'))

count = []
for g in genre_dict:
    count.extend(genre_dict[g])

print (len(count))
print (len(set(count)))
len(genre_dict['Jazz'])
len(genre_dict['Hip-Hop/Rap'])

# Create bar chart of genres and playlist counts
genre_counts = {}
for g in genre_dict:
    genre_counts[g] = len(genre_dict[g])

plt.figure(figsize=(15,7))
sns.barplot(list(genre_counts.keys()), list(genre_counts.values()))
plt.xticks(rotation=45)
plt.title('Playlist Count by Search Term (Genre)', fontsize=24)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)



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

artist_dict = pickle.load(open('artists.pkl', 'rb'))

new_remastered

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


new_remastered['genre'] = new_remastered.progress_apply(lambda row: label_genre(row, genre_dict), axis=1)

new_remastered = new_remastered.reset_index(drop=True)


pickle.dump(new_remastered, open('new_remastered.pkl', 'wb'))



new_remastered = pickle.load(open('new_remastered.pkl', 'rb'))


artist_genres = pd.DataFrame(new_remastered.groupby('artist_ID')['genre'].apply(list).reset_index())
artist_genres['genre'] = artist_genres.genre.progress_apply(lambda x: [key for key, value in Counter(x).most_common()][0])


artist_genres_tuples = [tuple(line) for line in artist_genres.to_numpy()]


failed = []
artist_info = {}
for artist in tqdm(artist_genres_tuples):
    time.sleep(.25)
    try:
        name = sp.artist(artist[0])['name']
    except:
        failed.append(artist)
        continue
    artist_info[name] = (artist[0], artist[1])


pickle.dump(artist_info, open('artist_info.pkl', 'wb'))



#------------------------------------------------------------------------------------------



new_remastered3 = pickle.load(open('new_remastered.pkl', 'rb'))


reader = Reader(rating_scale=(0, .2))
data = Dataset.load_from_df(new_remastered3[['artist_ID', 'playlist_ID', 'scaled']], reader)
trainset, testset = train_test_split(data, test_size=.01)


svd = SVD(n_factors=0, n_epochs=50, lr_all=0.009, reg_all=0.09)
final2 = svd.fit(trainset)
pickle.dump(final, open('final_model3.pkl', 'wb'))

predictions = final2.test(testset)

accuracy.rmse(predictions)
accuracy.mae(predictions)


param_grid = {'n_factors': [1, 0], 'n_epochs': [50, 60, 70], 'lr_all': [0.009, 0.01, 0.015], 'reg_all': [0.09, 0.1, 0.15]}
gs4 = GridSearchCV(SVD, param_grid=param_grid, cv=3, joblib_verbose=100)
gs4.fit(data)

gs4.best_score['rmse']
gs4.best_score['mae']
gs4.best_params['rmse']



#------------------------------------------------------------------------------------------



artist_info = pickle.load(open('artist_info_cut.pkl', 'rb'))


def get_predictions(artist, list_of_playlists, num_selections):
    rankings = []
    for playlist in list_of_playlists:
        prediction = final2.predict(artist, playlist)
        if prediction.r_ui != None:
            rankings.append((prediction.iid, prediction.r_ui))
        else:
            rankings.append((prediction.iid, prediction.est))
    sorted_rankings = sorted(rankings, reverse=True, key=lambda x: x[1])[:num_selections]
    return sorted_rankings


drake = get_predictions('3TVXtAsR1Inumwj472S9r4', genre_dict['Hip-Hop/Rap'], 10)

drake
youngthug = get_predictions('50co4Is1HCEo8bhOyUWKpn', genre_dict['Hip-Hop/Rap'], 10)

youngthug

uzi = get_predictions('4O15NlyKLIASxsJ0PrXPfz', genre_dict['Hip-Hop/Rap'], 2)
uzi

kidcudi = get_predictions('0fA0VVWsXO9YnASrzqfmYu', genre_dict['Hip-Hop/Rap'], 2)
kidcudi

lupe = get_predictions('01QTIT5P1pFP3QnnFSdsJf', genre_dict['Hip-Hop/Rap'], 2)
lupe

odesza = get_predictions('21mKp7DqtSNHhCAU2ugvUw', genre_dict['EDM'], 2)
odesza

flume = get_predictions('6nxWCVXbOlEVRexSbLsTer', genre_dict['EDM'], 2)
flume


garrix = get_predictions('60d24wfXkVzDSfLS6hyCjZ', genre_dict['EDM'], 2)
garrix



#------------------------------------------------------------------------------------------



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



#------------------------------------------------------------------------------------------



scope = 'playlist-modify-public'
redirect_uri = 'http://www.google.com/'
token = util.prompt_for_user_token(config.user,
                           scope,
                           client_id=config.client_id,
                           client_secret=config.client_secret,
                           redirect_uri=redirect_uri)


username = 'Rob'
playlist_name = username + "'s Mix"
if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    new_playlist = sp.user_playlist_create(config.user, playlist_name, description='Strictly bangers, brought to you by playlist.append()')
    results = sp.user_playlist_add_tracks(config.user, new_playlist['id'], playlist_songs)
else:
    print("Can't get token for", username)

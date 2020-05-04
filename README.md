# playlist.append()
### _Spotify playlist builder via collaborative filtering recommendation system_

## Goal
Allow for users to create unique Spotify playlists of songs similiar to the ones they already love, simply by entering the name of an artist(s) — discovering new music in the process.

## Premise
1. User inputs artist(s)
2. Recommendation system suggests playlists based on input
3. Takes random songs from a random selection of those recommended playlists
4. Formulates new playlist from those songs

## File Directory
* [playlist.py](https://github.com/ralterman/playlist.append/blob/master/playlist.py "playlist.py File") - full code
* [functions.py](https://github.com/ralterman/playlist.append/blob/master/functions.py "functions.py File") - just the essential functions   for running the program
* [main.py](https://github.com/ralterman/playlist.append/blob/master/main.py "main.py File") - main function to run the program in the       terminal
* [frontend.py](https://github.com/ralterman/playlist.append/blob/master/frontend.py "frontend.py") - code for Streamlit frontend site

## Prerequisites
[Spotipy](https://spotipy.readthedocs.io/en/2.9.0/ "Spotipy") — Python library for the Spotify Web API
 * Follow the instructions to install and get authorized before use
 * Create and register your app on [Spotify for Developers](https://developer.spotify.com/dashboard/ "Spotify for Developers") to obtain      your Client ID and Client Secret
 * We'll be using both the Client Credentials Flow and Authorization Code Flow

<p align="center"><img src="https://github.com/ralterman/playlist.append/blob/master/images/authorization.png"></p>
<p align="center"><img src="https://github.com/ralterman/playlist.append/blob/master/images/authorization2.png"></p>

## Data Preprocessing / Feature Engineering
* Started by scraping all playlists resulting from the queries of 126 genres from sp.recommendation_genre_seeds()
  * Can capture at most 5,000 results from each query*
* Cut that number down to 14 of what I deemed as the most popular genres after some EDA, Google searches, and my own intuition in efforts   to lower the amount of data due to time constraints
* Gathered the artists that appeared in each of these playlists and took note of how many songs in the playlist were by/with that artist
* Continued to cut down amount of data to improve recommendations:
  * Eliminated artists that were in fewer than 12 playlists (mean #), and removed the playlists that those artists appeared in
  * Set maximum percentage of songs by/with an artist in each playlist at 20%, meaning each playlist had to have at least 5 different         artists (got rid of playlists where greater percentages existed)
  * Removed all playlists that had less than 20 songs or greater than 500 songs
  * Ignored cover and piano versions of songs
* Ended up with __6,706 unique playlists and 17,421 unique artists__

<p align="center"><img src="https://github.com/ralterman/playlist.append/blob/master/images/genre_distribution.png"></p>

## More Feature Engineering
* Created dictionary, where the 14 genres were the keys and the values were a list of playlists in that genre to use for the predictions     function
* Marked each artist with a list of genres of the playlists he or she is in, ordered that list by occurences of each genre, and kept the     top occuring genre
* Created second dictionary with the artist's name as the key and a tuple of his/her artist ID and top genre as the value
  * This dictionary is used to convert user input to the artist ID and recommend playlists based on that artist's top genre

## Model
Collaborative Filtering with [Surprise SVD](https://surprise.readthedocs.io/en/stable/getting_started.html "Surprise SVD")
* Recommender that deals with rating data — in this case ratings = weights (percentage of songs in each playlist by/with that artist)
* Fills zeros in sparse matrix with estimated values given surrounding values

Optimal Parameters After Multiple Grid Searches:
* n_factors = 0, n_epochs = 50, lr_all = 0.009, reg_all = 0.09
* RMSE = 0.0146 (on scale of 0-1)

## How It Works
* Prediction function takes in artist ID, list of playlists in that artist's top genre, and the desired # of recommendations
* Returns sorted list of recommended playlists based on actual or estimated weights
* Separate functions are used to grab the songs from those playlists, keep a random number of songs from each of them, and put them into a   newly created Spotify playlist for the user

---
## [Demo](https://drive.google.com/file/d/11WMAuTqxGd26vTufGzA0QuFdOQsGF4Gu/view?usp=sharing)
Created frontend site for local usage with [Streamlit](https://docs.streamlit.io/) — an open-source Python library used to create custom web-apps for machine learning (see Demo link).

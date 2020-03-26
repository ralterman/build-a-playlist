# playlist.append()
### Spotify playlist builder via collaborative filtering recommendation system

## Goal
Allow for users to create unique Spotify playlists of songs similiar to the ones they already love, simply by entering the name of an artist(s) — discovering new music in the process.

## Premise
1. User inputs artist(s)
2. Recommendation system suggests playlists based on input
3. Takes random songs from a random selection of those recommended playlists
4. Formulates new playlist from those songs

## Prerequisites
* [Spotipy](https://spotipy.readthedocs.io/en/2.9.0/ "Spotipy") — Python library for the Spotify Web API
  * Follow the instructions to install and get authorized before use
  * Create and register your app on [Spotify for Developers](https://developer.spotify.com/dashboard/ "Spotify for Developers") to obtain     your Client ID and Client Secret
  * Will be using both the Client Credentials Flow and Authorization Code Flow

<p align="center"><img src="https://github.com/ralterman/playlist.append/blob/master/images/authorization.png"></p>

## Data
* Started by scraping all playlists resulting from the queries of 126 genres from sp.recommendation_genre_seeds()
  * Can capture at most 5,000 results from each query*
* Cut that number down to 14 of what I deemed as the most popular genres after some EDA, Google searches, and my own intuition in efforts   to lower the amount of data due to time constraints
* Gathered the artists that appeared in each of these playlists and took note of how many songs in the playlist were by/with that artist
* Continued to cut down amount of data:
  * Eliminated artists that were in fewer than 12 playlists (mean #), and removed the playlists that those artists appeared in
  * Set maximum percentage of songs by/with an artist in each playlist at 20%, meaning each playlist had to have at least 5 different         artists (got rid of playlists where greater percentages existed)
  * Removed all playlists that had less than 20 songs or greater than 500 songs
  * Ignored cover and piano versions of songs

<p align="center"><img src="https://github.com/ralterman/playlist.append/blob/master/images/genre_distribution.png"></p>


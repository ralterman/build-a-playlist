# playlist.append()
### Spotify playlist builder via collaborative filtering recommendation system

## Goal
Allow for users to create unique Spotify playlists of songs similiar to the ones they already love, simply by entering the name of an artist(s) — discovering new music in the process.

## Prerequisites
* [Spotipy](https://spotipy.readthedocs.io/en/2.9.0/ "Spotipy") — Python library for the Spotify Web API
  * Follow the instructions to install and get authorized before use
  * Create and register your app on [Spotify for Developers](https://developer.spotify.com/dashboard/ "Spotify for Developers") to obtain     your Client ID and Client Secret
  * Will be using both the Authorization Code Flow and Client Credentials Flow

## Data
* Started by scraping all playlists resulting from the queries of 126 genres from spotipy.recommendation_genre_seeds()
  * Can capture at most 5,000 results from each query
* Cut that number down to 14 of what I deemed as the most popular genres after some EDA, Google searches, and my own intuition in efforts to lower the amount of data due to time constraints

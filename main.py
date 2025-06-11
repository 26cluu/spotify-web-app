import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import json
import streamlit as st
from dotenv import load_dotenv
import os


st.title('spotbot')

#web api credentials
client_id = f"{os.getenv('id')}"
client_secret = f"{os.getenv('secret')}"
redirect_uri = 'http://localhost:8501/'
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public ugc-image-upload app-remote-control streaming user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read user-read-email user-read-private'


# client_creds = f'{client_id}:{client_secret}'
# client_creds_b64 = base64.b64encode(client_creds.encode())

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope=scope))


def configure():
    load_dotenv()

#meant to authorize user id for personal additions
def authorize():
    url = st.text_input('enter url')
    if url:
        code = sp.auth_manager.parse_response_code(url)
        auth_token = sp.auth_manager.get_access_token(code)
        st.success('authorized')
        return auth_token

#takes artist id and tries to search returns information if found
def find_artist(artist):
    # try: 
    results = sp.search(q='artist:' + artist, type='artist')
    if results['artists']['items'] != []:
        items = results['artists']['items'][0]['uri']
        return items
    else:
        st.write('artist not found')
        return None

#takes track name input and returns track items and info  
def find_track(track):
    results = sp.search(q='track:' + track, type='track')
    if results['tracks']['items'] != []:
        items = results['tracks']['items']
        return items
    else:
        st.write('artist not found')
        return None

#finds albums of a certain artist based of an inputted name
def find_album_artist(artist):
    uri = find_artist(artist)
    if uri == None:
        return None
    albums = sp.artist_albums(artist_id = uri, album_type='album', country=None, limit=None, offset=0)
    albums_real = albums['items']
    for album in albums_real:
        with st.expander(album['name']):
            tracks = sp.album_tracks(album['id'])
            tracks_real = tracks['items']
            for track in tracks_real:
                st.write(track['name'] + ' - ' + track['uri'][14:])
    
#grabs image of an artist
def artist_image(artist):
    results = sp.search(q='artist:' + artist, type='artist')
    if results['artists']['items'] == []:
        st.write('artist not found')
        return None
    items = results['artists']['items'][0]
    st.write(items['name']) 
    st.image(items['images'][0]['url'])

#grabs specified info of inputted artist and outputs that info
def artist_info(artist):
    uri = find_artist(artist)
    if uri == None:
        return None
    get_artist = sp.artist(artist_id=uri)
    artist_name = get_artist['name']
    artist_followers = get_artist['followers']['total']
    artist_genres = get_artist['genres']
    artist_genres_str = ' '.join(artist_genres)
    artist_popularity = get_artist['popularity']
    artist_spotify_url = get_artist['external_urls']['spotify']
    artist_image = get_artist['images'][0]['url']
    st.header(artist_name)
    st.write('Artist Followers: ' + str(artist_followers))
    st.write('Artist Genres: ' + artist_genres_str)
    st.write('Artist Popularity: ' + str(artist_popularity))
    st.write('spotify link: ' + artist_spotify_url)
    st.image(artist_image)

#grabs track info of specified song
def track_info(song):
    tracks = find_track(song)
    for track in tracks:
        with st.expander(track['name'] + ' - ' + track['artists'][0]['name'] + ' - ' + track['album']['name']):
            st.write('Artist: ' + track['artists'][0]['name'])
            st.write('Album: ' + track['album']['name'])
            st.write('Album Type: ' + track['album']['album_type'])
            st.write('Name: ' + track['name'])
            st.write('Release Date: ' + track['album']['release_date'])
            st.write('Popularity: ' + str(track['popularity']))
            st.write('Track id: ' + track['uri'][14:])
            st.image(track['album']['images'][0]['url'])
            st.audio(track['preview_url'])


#finds the playlists of current authorized user
def user_playlists():
    user_data = sp.current_user()
    user_id = user_data['id']
    playlists = sp.user_playlists(user_id)
    playlist_data = {}
    for playlist in playlists['items']:
        playlist_data[playlist['name']] = playlist['id']
    return playlist_data

#grabs current info of authorized user
def current_user_info():
    user_data = sp.current_user()
    user_id = user_data['id']
    playlists = sp.user_playlists(user_id)
    country = user_data['country']
    name = user_data['display_name']
    email = user_data['email']
    url = user_data['external_urls']['spotify']
    followers = str(user_data['followers']['total'])
    image = user_data['images'][0]['url']
    st.image(image)
    st.write('Country: ' + country)
    st.write('Name: ' + name)
    st.write('Email: ' + email)
    st.write('Url: ' + url)
    st.write('Followers: ' + followers)
    for playlist in playlists['items']:
        with st.expander(playlist['name']):
            # st.write(playlist)

            tracks = sp.user_playlist_tracks(playlist_id=playlist['id'])
            # st.write(tracks)
            for track in tracks['items']:
                st.write(track['track']['name'])


#adds playlsit to track 
def add_playlist():
    test = []
    playlists = user_playlists()
    names = playlists.keys()
    entry = st.selectbox('choose which playlist you want to add to', options = names)
    track_id = st.text_input('enter track id')
    save_button = st.button('save')
    if save_button:
        test.append(track_id)
        sp.playlist_add_items(playlists[entry], test)
        st.success('added playlist')

#main function for everything
def main():
    configure()
    artist = st.sidebar.text_input('enter artist')
    if st.sidebar.button('authorize'):
        auth_token = authorize()
    if st.sidebar.button('find albums'):
        find_album_artist(artist)
    if st.sidebar.button('artist photo'):
        artist_image(artist)
    if st.sidebar.button('artist info'):
        artist_info(artist)
    if st.sidebar.button('current user'):
        current_user_info()
    song = st.sidebar.text_input('enter track')
    if st.sidebar.button('find track'):
        track_info(song)
    tab1, tab2= st.tabs(['home', 'add track to playlist'])
    with tab1:
        current_user_info()
    with tab2:
        add_playlist()





if __name__ == '__main__':
    main()



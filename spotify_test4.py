import spotipy
import spotipy.oauth2 as oauth2

credentials = oauth2.SpotifyClientCredentials(
        client_id='fbb5700daf9a431ba8e4130b6b2e1a90',
        client_secret='a16b2910bc2644f1a95de6a88356f23d')

token = credentials.get_access_token()
spotify = spotipy.Spotify(auth=token)
spotify.start_playback('Dynamite')
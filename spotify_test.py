import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
 
cid = 'fbb5700daf9a431ba8e4130b6b2e1a90'
secret = 'a16b2910bc2644f1a95de6a88356f23d'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


result=sp.search("coldplay",limit=1,type='artist')
pprint.pprint(result)
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials 
import pprint 
class Spotify_audio_features: 
    def __init__(self): 
        # initial setting 
        cid = 'fbb5700daf9a431ba8e4130b6b2e1a90' 
        secret = 'a16b2910bc2644f1a95de6a88356f23d' 
        client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def get_features(self, song): 
        # get track id information 
        track_info = self.sp.search(q=song, type='track', market='JP') 
        track_id = track_info["tracks"]["items"][0]["id"] 
        # get audio_feature 
        features = self.sp.audio_features(tracks=[track_id]) 
        acousticness = features[0]["acousticness"] 
        danceability = features[0]["danceability"] 
        energy = features[0]["energy"] 
        liveness = features[0]["liveness"] 
        loudness = features[0]["loudness"] 
        valence = features[0]["valence"] 
        mode = features[0]["mode"] 
        result = {"acousticness" : acousticness, 
        "danceability" : danceability, 
        "energy" : energy, 
        "liveness" : liveness, 
        "loudness" : loudness, 
        "valence" : valence, 
        "mode" : mode} 
        return result


spot_item=Spotify_audio_features
pprint.pprint(spot_item.get_features('Dynamite'))



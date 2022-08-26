import os
import requests
from tkinter import *
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class App:
    
    def __init__(self):
        
        self.root = Tk()
        self.root.title('Nostalgia Machine')
        self.root.config(padx=20, pady=20)
        self.root.resizable(False, False)
        self.root.config(bg='whitesmoke')

        self.main_label = Label(text='Nostalgia Machine', bg='whitesmoke', font=('Courier New', 24, 'bold'))
        self.main_label.grid(column=0, row=0, pady=40, columnspan=2)

        self.sub_label = Label(text='Enter a date (YYYY-MM-DD): ', bg='whitesmoke', font=('Courier New', 12, 'normal'))
        self.sub_label.grid(column=0, row=1, pady=0, columnspan=2)

        self.date_entry = Entry(bg='whitesmoke', highlightbackground='whitesmoke')
        self.date_entry.grid(column=0, row=2, pady=10)

        self.enter_button = Button(text='Enter', bg='whitesmoke', highlightbackground='whitesmoke', command=self.create_playlist)
        self.enter_button.grid(column=1, row=2)
    
    
    def spotify_auth(self):
        
        load_dotenv()
        SPOTIFY_ID = os.getenv('CLIENT_ID')
        SPOTIFY_SECRET = os.getenv('CLIENT_SECRET')
        scope = "playlist-modify-private"
        spotify_init = spotipy.Spotify(
                                       auth_manager=SpotifyOAuth(
                                                                 client_id=SPOTIFY_ID, 
                                                                 client_secret=SPOTIFY_SECRET, 
                                                                 redirect_uri='https://example.com/',  
                                                                 scope=scope,
                                                                 show_dialog=True,
                                                                 cache_path="token.txt"
                                                                 )
                                       )
        return spotify_init
        
        
    def create_playlist(self):
        
        sp = self.spotify_auth()
        user = sp.me()['display_name']
    
        url = f"https://www.billboard.com/charts/hot-100/{self.date_entry.get()}/"
        response = requests.get(url)
        contents = response.text
        soup = BeautifulSoup(contents, 'html.parser')
        song_data = soup.select("li h3")
        artist_data = soup.find_all(name="span", class_='c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only')
        songs = [song.text.replace('\n', '').replace('\t', '') for song in song_data[1:100]]
        artists = [artist.text.replace('\n', '').replace('\t', '') for artist in artist_data]
        
        results = []
        for song, artist in zip(songs, artists):
            try:
                song_uri = sp.search(q=f"track: {song} artist: {artist}", type='track')['tracks']['items']
            except Exception:
                print(f'{song} skipped.')
            
            if len(song_uri) > 0:
                results.append(song_uri[0]['uri'])
                
        new_playlist = sp.user_playlist_create(user=user, name=self.date_entry.get(), public=False, collaborative=False, description='https://github.com/boolin9')
        sp.user_playlist_add_tracks(user=user, playlist_id=new_playlist['id'], tracks=results)



if __name__ == "__main__":
    app = App()
    app.root.mainloop()
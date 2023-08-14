import pydub
from pydub.playback import play
import librosa
import threading
import time

# get all mp3 files in the tracks folder

from os import listdir
from os.path import isfile, join

mypath = "tracks/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

playlist = onlyfiles
print(playlist)


def play_music(track) :
    play(track)


def get_tempo(track) :
    y, sr = librosa.load(track)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return round(tempo, 0)


def handle_playlist(playlist) :
    threads = []
    fade_duration = 5000
    desired_duration = 30000
    desired_tempo = 144

    for music in playlist :

        music_path = "tracks/" + music
        music_name = music.split(".")[0]

        track = pydub.AudioSegment.from_mp3(music_path)[:desired_duration]
        track = track.fade_in(fade_duration).fade_out(fade_duration)

        music_tempo = get_tempo(music_path)
        rate = desired_tempo / music_tempo
        print(rate)

        if rate != 1 :
            print("\nAdjusting tempo to", rate * music_tempo, "for", music_name)
            track = track.speedup(playback_speed=rate, chunk_size=150, crossfade=25)

        track_duration = round(track.duration_seconds, 0)

        print("Playing", music_name, "Duration:", track_duration, "s", "Tempo:", music_tempo * rate, "bpm")

        # Start the next track in a separate thread
        thread = threading.Thread(target=play_music, args=(track,))
        thread.start()
        threads.append(thread)

        # Wait for the fade out to complete before moving on to the next track
        time.sleep(abs((track.duration_seconds * 1000 - fade_duration) / 1000))

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

handle_playlist(playlist)

import pydub
from pydub.playback import play
import librosa
import soundfile as sf
import threading
import time
import numpy as np
from os import listdir, remove
from os.path import isfile, join

mypath = "tracks/"
playlist = [f for f in listdir(mypath) if isfile(join(mypath, f))]


def play_music(track):
    play(track)


def delete_tmp_files(directory):
    # remove file named temp.flac
    try:
        remove(f"{directory}/temp.flac")
    except FileNotFoundError:
        pass


def get_tempo(track):
    y, sr = librosa.load(track)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = round(tempo, 0)
    print(f"Actual tempo : {tempo}")
    return tempo


def adjust_tempo(track, rate):
    y, sr = librosa.load(track)
    y_changed = librosa.effects.time_stretch(y, rate=rate)
    temp_filename = f"tmps/temp.flac"
    sf.write(temp_filename, y_changed, sr, format='FLAC')
    return pydub.AudioSegment.from_file(temp_filename, format='FLAC')


def handle_playlist(playlist, fade_duration=5000, desired_duration=30000, desired_tempo=200):
    threads = []

    for music in playlist:
        music_path = mypath + music
        music_name = music.split(".")[0]

        # Charger le fichier audio et ajuster la durée
        track = pydub.AudioSegment.from_mp3(music_path)[:desired_duration]
        track = track.fade_in(fade_duration).fade_out(fade_duration)

        # Obtenir le tempo et ajuster le tempo si nécessaire
        music_tempo = get_tempo(music_path)
        rate = desired_tempo / music_tempo
        rate = round(rate, 2)
        print(f"Rate : {rate}")

        if rate != 1.0:
            print(f"\nAdjusting tempo to {desired_tempo} for {music_name}")
            track = adjust_tempo(music_path, rate)
            # Ajuster la durée après avoir modifié le tempo
            track = track[:desired_duration]
            track = track.fade_in(fade_duration).fade_out(fade_duration)

        track_duration = round(track.duration_seconds, 0)
        print(
            f"Playing : {music_name}\nDuration : {track_duration}s\nTempo : {music_tempo * rate} bpm"
        )

        # Lancer la lecture de la piste dans un thread séparé
        thread = threading.Thread(target=play_music, args=(track,))
        thread.start()
        threads.append(thread)

        # Attendre que le fondu se termine avant de passer à la piste suivante
        time.sleep((track.duration_seconds * 1000 - fade_duration) / 1000)

    # Attendre que tous les threads se terminent
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    print(playlist)
    handle_playlist(playlist)
    delete_tmp_files("tmps")

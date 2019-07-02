import file
from pysynth import SoundPySynth

def text_2_music():
    print("###### Welcome to the TextToMusic Program V2 ######")

    filename = "text"
    filepath = "./data/" + filename + ".txt"
    f = file.TextFileToMusic(filepath)
    s = SoundPySynth(octave=4)

    output_file = "./output/" + filename + "_"

    # print(f.get_words_values(f="mean"))

    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_flute.wav", bpm=230, version="a")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_piano.wav", bpm=230, version="b")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_bowed.wav", bpm=230, version="c")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_woodwind.wav", bpm=230, version="d")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_rhodes.wav", bpm=230, version="e")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_percs.wav", bpm=230, version="p")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_strings.wav", bpm=180, version="s")

    '''
    Join wav files together (one after the other)
    '''
    # sound1 = pydub.AudioSegment.from_wav("1_b_mean.wav")
    # sound2 = pydub.AudioSegment.from_wav("1_p_mean.wav")
    # sound3 = pydub.AudioSegment.from_wav("1_s_mean.wav")
    # combined_sounds = sound1 + sound2 + sound3 
    # combined_sounds.export("joinedFile.wav", format="wav")

if __name__ == '__main__':
    text_2_music()

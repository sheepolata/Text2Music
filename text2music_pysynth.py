import PySynth.pysynth as psa
import PySynth.pysynth_b as psb
import PySynth.pysynth_c as psc
import PySynth.pysynth_d as psd
import PySynth.pysynth_e as pse
import PySynth.pysynth_p as psp
import PySynth.pysynth_s as pss
# Synth   Synthesis method    Approximate timbre  Note decay  Needs NumPy?
# A   additive (3 sine waves)     flute, organ, piano     variable (depends on note length)   no
# B   additive (5 sine waves)     acoustic piano  medium  yes
# C   subtractive (sawtooth wave)     bowed string, analog synth pad  none    no
# D   subtractive (square wave)   woodwind, analog synth lead     none    no
# E   FM/phase modulation (6 sine waves)  DX7 Rhodes piano    medium  yes
# P   subtractive (white noise)   untuned percussion hit  very fast   no
# S   Karplus-Strong (physical modeling)  plucked string, guitar, koto    fast    yes

import math
import pyaudio
import wave
import pydub

import file

# import pysynth_b as psb # a, b, e, and s variants available

# ''' (note, duration)
# Note name (a to g), then optionally a '#' for sharp or
# 'b' for flat, then optionally the octave (defaults to 4).
# An asterisk at the end means to play the note a little 
# louder.  Duration: 4 is a quarter note, -4 is a dotted 
# quarter note, etc.'''
# song = (
#   ('c', 4), ('c*', 4), ('eb', 4), 
#   ('g#', 4),  ('g*', 2), ('g5', 4),
#   ('g5*', 4), ('r', 4), ('e5', 16),
#   ('f5', 16),  ('e5', 16),  ('d5', 16),
#   ('e5*', 4) 
# )

# # Beats per minute (bpm) is really quarters per minute here
# psb.make_wav(song, fn = "danube.wav", leg_stac = .7, bpm = 180)


#PySynth Handling class
class SoundPySynth(object):
    """docstring for SoundPySynth"""
    def __init__(self, octave=4):
        super(SoundPySynth, self).__init__()

        self.octave = octave

        _notes = ["c", "d", "e", "f", "g", "a", "b"]
        self.notes = []
        for n in _notes:
            self.notes.append(n + "b" + str(self.octave))
            self.notes.append(n + str(self.octave))
            self.notes.append(n + "#" + str(self.octave))

        # self.notes = ["c"]

        # self.possible_durations = [-16, -12, -8, -4, 4, 8, 12, 16]
        self.possible_durations = [4, 2, 1]

    def generate_song(self, values, length):
        song = []

        duration_index_max = float(len(self.possible_durations) - 1)
        note_index_max     = float(len(self.notes) - 1)

        values_min = float(min(values))
        values_max = float(max(values))

        len_min = float(min(length))
        len_max = float(max(length))

        for i in range(len(values)):
            v = int(math.floor((values[i] - values_min)/(values_max - values_min) * note_index_max))
            l = int(math.floor((length[i] - len_min)/(len_max - len_min) * duration_index_max))
            song.append((self.notes[v], self.possible_durations[l]))

        return tuple(song)

    def generate_wav(self, values, length, filepath="out.wav", bpm=180, version="a"):
        song = self.generate_song(values, length)
        if version == "a":
            psa.make_wav(song, fn = filepath, bpm = bpm)
        elif version == "b":
            psb.make_wav(song, fn = filepath, bpm = bpm)
        elif version == "c":
            psc.make_wav(song, fn = filepath, bpm = bpm)
        elif version == "d":
            psd.make_wav(song, fn = filepath, bpm = bpm)
        elif version == "e":
            pse.make_wav(song, fn = filepath, bpm = bpm)
        elif version == "p":
            psp.make_wav(song, fn = filepath, bpm = bpm)
        elif version == "s":
            pss.make_wav(song, fn = filepath, bpm = bpm)
        else:
            psa.make_wav(song, fn = filepath, bpm = bpm)





        

def main():
    print("###### Welcome to the TextToMusic Program V2 ######")

    filename = "text"
    filepath = "./data/" + filename + ".txt"
    f = file.TextFileToMusic(filepath)
    s = SoundPySynth(octave=4)

    output_file = "./output/" + filename + "_"

    # print(f.get_words_values(f="mean"))

    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_flute.wav", bpm=230, version="a")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_piano.wav", bpm=230, version="b")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_bowed.wav", bpm=230, version="c")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_woodwind.wav", bpm=230, version="d")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_rhodes.wav", bpm=230, version="e")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_percs.wav", bpm=230, version="p")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel_strings.wav", bpm=180, version="s")

    '''
    Join wav files together (one after the other)
    '''
    # sound1 = pydub.AudioSegment.from_wav("1_b_mean.wav")
    # sound2 = pydub.AudioSegment.from_wav("1_p_mean.wav")
    # sound3 = pydub.AudioSegment.from_wav("1_s_mean.wav")
    # combined_sounds = sound1 + sound2 + sound3 
    # combined_sounds.export("joinedFile.wav", format="wav")

if __name__ == '__main__':
    main()
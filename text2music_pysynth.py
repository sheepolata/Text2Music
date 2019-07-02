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
import numpy as np

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

        self.min_octave = 2
        self.max_octave = 6
        # self.octave = octave
        self.octave = max(self.min_octave, min(octave, self.max_octave))

        self.initialise_notes()

        # self.notes = ["c"]

        # self.possible_durations = [-16, -12, -8, -4, 4, 8, 12, 16]
        self.possible_durations = [4, 2, 1, 0.5]

    def initialise_notes(self):
        _notes = ["c", "d", "e", "f", "g", "a", "b"]
        self.notes = []
        for n in _notes:
            # self.notes.append(n + "b" + str(self.octave))
            self.notes.append(n + str(self.octave))
            # self.notes.append(n + "#" + str(self.octave))

    def generate_song(self, values, length):
        song = []

        duration_index_max = float(len(self.possible_durations) - 1)
        note_index_max     = float(len(self.notes) - 1)

        values_min = float(min(values))
        values_max = float(max(values))

        len_min = float(min(length))
        len_max = float(max(length))

        initial_note     = np.random.choice(self.notes)
        initial_duration = np.random.choice(self.possible_durations)

        song.append((initial_note, initial_duration))

        for i in range(len(values)):
            v = int(math.floor((values[i] - values_min)/(values_max - values_min) * note_index_max))
            l = int(math.floor((length[i] - len_min)/(len_max - len_min) * duration_index_max))
            song.append((self.notes[v], self.possible_durations[l]))

        return tuple(song)

    def generate_song_chain(self, values, length, return_chance=0.00):
        song = []

        duration_index_max = float(len(self.possible_durations) - 1)
        note_index_max     = float(len(self.notes) - 1)

        values_min = float(min(values))
        values_max = float(max(values))

        len_min = float(min(length))
        len_max = float(max(length))

        current_note_index = np.random.randint(0, len(self.notes))
        initial_octave = self.octave
        initial_note_index = current_note_index
        initial_note       = self.notes[initial_note_index]
        # print("init", current_note_index)

        initial_duration = np.random.choice(self.possible_durations)

        song.append((initial_note, initial_duration))

        prev_value = values[0]
        prev_len   = length[0]
        for i in range(1, len(values)):
            # n = int(math.floor((values[i] - values_min)/(values_max - values_min) * note_index_max))
            curr_value = values[i]
            curr_len   = length[i]

            value_diff = abs(curr_value - prev_value)

            sign = 1 if value_diff%2==0 else -1

            if value_diff <= 3:
                current_note_index = current_note_index
            if value_diff <= 7:
                current_note_index = current_note_index + sign
            else:
                current_note_index = current_note_index + sign*2

            if np.random.random() < return_chance:
                print("RETURN", i)
                current_note_index = initial_note_index
                self.octave = initial_octave
                self.initialise_notes()
            elif current_note_index > len(self.notes)-1:
                if self.octave < self.max_octave:
                    current_note_index = current_note_index%(len(self.notes)-1)
                    self.octave += 1
                    self.initialise_notes()
                else:
                    current_note_index = len(self.notes)-1
            elif current_note_index < 0:
                if self.octave > self.min_octave:
                    current_note_index = len(self.notes)-1 + current_note_index
                    self.octave -= 1
                    self.initialise_notes()
                else:
                    current_note_index = 0

            # print(current_note_index, " ", self.octave)

            l = int(math.floor((length[i] - len_min)/(len_max - len_min) * duration_index_max))
            
            song.append((self.notes[current_note_index], self.possible_durations[l]))

            prev_value = curr_value
            prev_len = curr_len

        # for s in song:
        #     print(s)
        # song[len(song)-1] = (song[len(song)-1][0], 0.5)

        return tuple(song)

    def generate_wav(self, values, length, generation="base", filepath="out.wav", bpm=180, version="a"):
        if generation == "chain":
            song = self.generate_song_chain(values, length)
        else:
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

    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_flute.wav", bpm=230, version="a")
    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_piano.wav", bpm=230, version="b")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_bowed.wav", bpm=230, version="c")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_woodwind.wav", bpm=230, version="d")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_rhodes.wav", bpm=230, version="e")
    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), generation="chain", filepath=output_file+"channel_percs.wav", bpm=230, version="p")
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
    main()
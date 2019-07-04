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

import time, _thread

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
print('')


#PySynth Handling class
class SoundPySynth(object):
    """docstring for SoundPySynth"""
    def __init__(self, octave=4, bpm=180, generation_type="chain"):
        super(SoundPySynth, self).__init__()
        self.bpm = bpm
        self.generation_type = generation_type

        self.min_octave = 2
        self.max_octave = 6
        # self.octave = octave
        self.octave = max(self.min_octave, min(octave, self.max_octave))

        self.initialise_notes()

        # self.notes = ["c"]

        # self.possible_durations = [-16, -12, -8, -4, 4, 8, 12, 16]
        self.possible_durations = [4, 2, 1, 0.5]

        self.wavpath = None
        self.used_words = []
        self.song = []

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

        for i in range(1, len(values)):
            v = int(math.floor((values[i] - values_min)/(values_max - values_min) * note_index_max))
            l = int(math.floor((length[i] - len_min)/(len_max - len_min) * duration_index_max))
            song.append((self.notes[v], self.possible_durations[l]))

        return tuple(song)

    def generate_song_chain(self, values, length, return_chance=0.00):
        song = []

        duration_index_max = float(len(self.possible_durations) - 1)
        note_index_max     = float(len(self.notes) - 1)

        # print(values)
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
                # print("RETURN", i)
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

    def generate_wav(self, f, version='a', filepath="out", markov=False):
        ws = f.words
        if markov:
            ws, lines = f.wordListFromMarkov(length=f.markov_length)
            r = open("./output/markov_" + f.title + "_" + str(f.markov_seed) + ".txt", "w", encoding='utf-8')
            disp_i = 0
            for i, l in enumerate(lines):
                disp_i = i
                print("Write text... {0}%\r".format(round((float(i)/float(len(lines)))*100.0, 2)), end='', flush=True)
                r.write(l + '\n')
            print("Write text... {0}% - done\r".format(round((float(disp_i+1)/float(len(lines)))*100.0, 2)), end='', flush=True)
            print('')
            print("Results wrote to" + "./output/markov_" + f.title + "_" + str(f.markov_seed) + ".txt")

            r.close()

        self.used_words = ws

        if self.generation_type == "chain":
            self.song = self.generate_song_chain(f.get_words_values(f="mean", words=ws), f.get_duration_factors(f="len", words=ws))
        else:
            self.song = self.generate_song(f.get_words_values(f="mean", words=ws), f.get_duration_factors(f="len", words=ws))

        txt_markov = "_markov_"+str(f.markov_seed) if markov else ""

        self.wavpath = filepath + "_" + self.generation_type
        if version == "a":
            self.wavpath += "_flute"+txt_markov+".wav"
            psa.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "b":
            self.wavpath += "_piano"+txt_markov+".wav"
            psb.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "c":
            self.wavpath += "_bowed"+txt_markov+".wav"
            psc.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "d":
            self.wavpath += "_woodwind"+txt_markov+".wav"
            psd.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "e":
            self.wavpath += "_rhodes"+txt_markov+".wav"
            pse.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "p":
            self.wavpath += "_percs"+txt_markov+".wav"
            psp.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "s":
            self.wavpath += "_strings"+txt_markov+".wav"
            pss.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        else:
            self.wavpath += txt_markov+".wav"
            psa.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')

        # return self.wavpath

    def generate_orchestra(self, f, offset_duration=8, version='a', filepath="out", markov=False):
        ws = f.words
        if markov:
            ws, lines = f.wordListFromMarkov(length=f.markov_length)
            r = open("./output/markov_" + f.title + "_" + str(f.markov_seed) + ".txt", "w", encoding='utf-8')
            disp_i = 0
            for i, l in enumerate(lines):
                disp_i = i
                print("Write text... {0}%\r".format(round((float(i)/float(len(lines)))*100.0, 2)), end='', flush=True)
                r.write(l + '\n')
            print("Write text... {0}% - done\r".format(round((float(disp_i+1)/float(len(lines)))*100.0, 2)), end='', flush=True)
            print('')
            print("Results wrote to" + "./output/markov_" + f.title + "_" + str(f.markov_seed) + ".txt")

            r.close()

        self.used_words = ws

        word_values, duration_factor = f.get_words_values(f="mean", words=ws), f.get_duration_factors(f="len", words=ws)

        if self.generation_type == "chain":
            self.song = self.generate_song_chain(word_values, duration_factor)
        else:
            self.song = self.generate_song(word_values, duration_factor)

        addition_wav_files = []
        instruments_to_add = [(psp.make_wav, 1, 4), (pss.make_wav, 2, 1)]

        offset_notes = []
        for i in range(offset_duration):
            offset_notes.append(('r', 2))

        self.song = offset_notes + list(self.song)
        self.song = list(self.song) + offset_notes
        self.song = tuple(self.song)

        # print(self.song)
        self.wavpath = filepath + "_" + self.generation_type
        txt_markov = "_markov_"+str(f.markov_seed) if markov else ""
        self.wavpath += txt_markov+".wav"

        if version == "b":
            self.wavpath += "_piano"+txt_markov+".wav"
            psb.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        elif version == "e":
            self.wavpath += "_rhodes"+txt_markov+".wav"
            pse.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')
        else:
            self.wavpath += txt_markov+".wav"
            psa.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
            print('')


        for index, ita in enumerate(instruments_to_add):
            a = np.random.randint(0, max(len(word_values)-int(offset_duration*ita[1]), 1))
            # b = np.random.randint(a+int(offset_duration*ita[1]), len(word_values))
            loop_values  = word_values[a:min(a+int(offset_duration*ita[1]), len(word_values))]
            loop_factors = duration_factor[a:min(a+int(offset_duration*ita[1]), len(duration_factor))]
            # print(loop_values, len(loop_values), a, a+int(offset_duration*ita[1]))
            # if self.generation_type == "chain":
            #     loop_song = self.generate_song_chain(loop_values, loop_factors)
            # else:
            loop_song = self.generate_song(loop_values, loop_factors)
            #SET THE NOTES TO BE REGULAR
            loop_song = tuple([(n[0], ita[2]) for n in loop_song])
            # print(loop_song)

            nb_beat = np.sum([(1./n[1])*4. for n in self.song])
            loop_filepath_percs = filepath + "_background" + str(index) + "_" + txt_markov + ".wav"
            ita[0](loop_song, fn=loop_filepath_percs, bpm = self.bpm, repeat=int(nb_beat/ np.sum([(1./n[1])*4. for n in loop_song]) ))
            print('')
            addition_wav_files.append(loop_filepath_percs)

        sound1 = pydub.AudioSegment.from_wav(self.wavpath)

        for fp in addition_wav_files:
            sound2 = pydub.AudioSegment.from_wav(fp)
            # combined_sounds = sound1 + sound2 #Check OVERLAY
            sound1 = sound1.overlay(sound2, gain_during_overlay=4)

        import os
        print("delete " + self.wavpath)
        os.remove(self.wavpath)
        for fp in addition_wav_files:
            print("delete " + fp)
            os.remove(fp)

        sound1.export(filepath + "_orchestra_" + txt_markov + ".wav", format="wav")
        print("Quality music saved to {} ... Enjoy listening !".format(filepath + "_orchestra_" + txt_markov + ".wav"))





    def playWavWithDispay(self):
        if(self.wavpath == None):
            print("No Wave Path stored...")
            return

        print("Play {} ... Enjoy !".format(self.wavpath))
        #define stream chunk   
        chunk = 1024  

        #open a wav format music  
        wavfile = wave.open(self.wavpath, mode='rb')
        #instantiate PyAudio  
        p = pyaudio.PyAudio()  
        #open stream  
        stream = p.open(format = p.get_format_from_width(wavfile.getsampwidth()),  
                        channels = wavfile.getnchannels(),  
                        rate = wavfile.getframerate(),  
                        output = True)  
        #read data  
        data = wavfile.readframes(chunk)  

        wav_duration_sec = wavfile.getnframes()/wavfile.getframerate()
        wav_duration_min = wav_duration_sec / 60.
        nb_beat = np.sum([(1./n[1])*4. for n in self.song])
        bps = float(self.bpm) / 60.
        # beat_duration_sec = 1./bps
        beat_duration_min = wav_duration_min / nb_beat
        beat_duration_sec = wav_duration_sec / nb_beat

        print("dsec = {}, dmin = {}, bpm = {}, nb_beat = {}, bps = {}, bdm = {}, bds = {}".format(wav_duration_sec, wav_duration_min, self.bpm, nb_beat, bps, beat_duration_min, beat_duration_sec))

        
        _thread.start_new_thread( print_song, (self.song, self.used_words, beat_duration_sec ) )

        #play stream  
        while data:  
            stream.write(data)  
            data = wavfile.readframes(chunk)  


        #stop stream  
        stream.stop_stream()  
        stream.close()  

        #close PyAudio  
        p.terminate() 

        print("Thank you for listening, bye bye !")


def print_song(song, words, beat_duration):
    # total_t = time.time()
    if len(song) != len(words):
        print("song size {} != words size {}".format(len(song), len(words)))
        return

    to_print  = ""
    max_char_per_line = 70
    beat = 0
    for i in range(len(song)):
        offset_t = time.time()
        note = song[i]
        # word = words[i]
        to_print += words[i] + " "
        if(len(to_print) > max_char_per_line):
            to_print += '\n'
            print("{}\r".format(to_print), end='', flush=True)
            to_print = ""
        else:
            pass
            print("{}\r".format(to_print), end='', flush=True)

        # beat += note[1]
        # print(beat)

        i += 1
        offset_t = time.time() - offset_t
        # print(((1.0)/float(note[1])) * (beat_duration*4), note[1])
        # time.sleep( ((1.0/float(note[1]))) - offset_t)
        # time.sleep( ((1.0/float(note[1])) * (beat_duration*4.)) - offset_t)
        # time.sleep( ((1.0/float(note[1])) / (beat_duration*4.)) - offset_t)
        time.sleep( (((beat_duration*4.)/float(note[1]))) - offset_t)
    # print(time.time() - total_t)

def print_time(threadName, delay):
    count = 0
    while count < 5:
        time.sleep(delay)
        count += 1
        print ("{}: {}".format( threadName, time.ctime(time.time()) ))

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
import glob
import os
import random
import matplotlib.pyplot as plt

from pydub import AudioSegment as audio
import numpy as np
from os import path
import time, _thread
import platform

# import ValueError

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
        self._initialise_samples()
        # self.notes = ["c"]

        # self.possible_durations = [-16, -12, -8, -4, 4, 8, 12, 16]
        self.possible_durations = [4, 2, 1, 0.5]

        self.wavpath = None
        self.used_words = []
        self.song = []


    def _initialise_samples(self):
        # Works with nested directories as well
        sample_files = glob.glob("./data/samples/**/*.wav", recursive=True)
        self.samples = {}
        for f in sample_files:
            f_name = path.splitext(path.basename(f))[0]
            self.samples[f_name] = audio.from_wav(f)

    def initialise_notes(self):
        _notes = ["c", "d", "e", "f", "g", "a", "b"]
        self.notes = []
        for n in _notes:
            # self.notes.append(n + "b" + str(self.octave))
            self.notes.append(n + str(self.octave))
            # self.notes.append(n + "#" + str(self.octave))

        self.all_notes = []
        for o in range(self.min_octave, self.max_octave+1):
            for n in _notes:
                self.all_notes.append('{}{}'.format(n ,o))


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

    def generate_song_chain(self, values, length, return_chance=0.35, fval="mean"):
        song = []

        if len(values) != len(length):
            # print(len(values), "!=", len(length))
            raise(ValueError("Error " + str(len(values)) + " != " + str(len(length))))

        duration_index_max = float(len(self.possible_durations) - 1)
        note_index_max     = float(len(self.notes) - 1)

        len_min = float(min(length))
        len_max = float(max(length))

        current_note_index = np.random.randint(0, len(self.notes))
        initial_octave     = self.octave
        initial_note_index = current_note_index
        initial_note       = self.notes[initial_note_index]

        initial_duration = np.random.choice(self.possible_durations)

        song.append((initial_note, initial_duration))

        if fval == "spacy":
            # print(len(values), values)

            for i in range(0, len(values)):
                _v = values[i][0]

                # sign = 1 if _v > 0.35 else -1
                # sign = 1 if _v > 0.4 else -1
                # sign = 1 if np.random.random() > 0.5 else -1
                
                positive_pos_ = ["VERB", "NUM", "NOUN", "SYM", "ADP"]
                sign = 1 if values[i][1] in positive_pos_ else -1

                if _v > 0.75:
                    current_note_index = current_note_index
                if _v >= 0.25:
                    current_note_index = current_note_index + sign
                else:
                    current_note_index = current_note_index + sign*2

                mod = int(len(values)/20) if int(len(values)/20) > 0 else 1
                # if i%int(len(values)/10) == 0 and np.random.random() < return_chance:
                if i%mod == 0:
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

                l = int(math.floor((length[i] - len_min)/(len_max - len_min) * duration_index_max))
                
                song.append((self.notes[current_note_index], self.possible_durations[l]))

        else:
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

                if i%int(len(values)/10) == 0 and np.random.random() < return_chance:
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
            _f = "spacy"
            self.song = self.generate_song_chain(f.get_words_values(f=_f, words=ws), f.get_duration_factors(f="len", words=ws), fval=_f)
        else:
            self.song = self.generate_song(f.get_words_values(f="mean", words=ws), f.get_duration_factors(f="len", words=ws))

        txt_markov = "_markov_"+str(f.markov_seed) if markov else ""
        self.wavpath = filepath + "_" + self.generation_type
        if version == "a":
            self.wavpath += "_flute"+txt_markov+".wav"
            psa.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        elif version == "b":
            self.wavpath += "_piano"+txt_markov+".wav"
            psb.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        elif version == "c":
            self.wavpath += "_bowed"+txt_markov+".wav"
            psc.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        elif version == "d":
            self.wavpath += "_woodwind"+txt_markov+".wav"
            psd.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        elif version == "e":
            self.wavpath += "_rhodes"+txt_markov+".wav"
            pse.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        elif version == "p":
            self.wavpath += "_percs"+txt_markov+".wav"
            psp.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        elif version == "s":
            self.wavpath += "_strings"+txt_markov+".wav"
            pss.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        else:
            self.wavpath += txt_markov+".wav"
            psa.make_wav(self.song, fn = self.wavpath, bpm = self.bpm)
        
        print('')

        return self.wavpath

    def generate_orchestra(self, f, offset_duration=8, version='a', filepath="out", markov=False):
        wavpath = self.generate_wav(f, version, filepath, markov)
        txt_markov = "_markov_"+str(f.markov_seed) if markov else ""
        harmony = audio.from_wav(wavpath)
        # Duration of a quarter for a 4/4 time signature
        quarter_duration = 1000 / (self.bpm / 60)
        # Add a silent of `offset_duration' quarter at the start
        harmony  = audio.silent(quarter_duration*offset_duration) + harmony 

        # list of accompaniments. 
        # Each make up a bar, composed of 4 beats. 
        accompaniment = random.choice([
            Beat.get_beat_simple(),
            Beat.get_beat_simple2(),
            Beat.get_beat_rap()
            # Beat.get_beat_test()
        ])

        # Create an empty bar
        mashup = audio.silent(duration=quarter_duration * accompaniment['length'])

        for sample_name, start in accompaniment['rhythm']:
            mashup = mashup.overlay(self.samples[sample_name], position=start*quarter_duration)

        #Reduce mashup volume and overlay
        mashup = mashup - 12
        harmony = harmony.overlay(mashup, loop=True, gain_during_overlay=0) 

        os.remove(self.wavpath)
        self.wavpath = filepath + "_orchestra" + txt_markov + ".wav"
        harmony.export(self.wavpath, format="wav")
        print("Quality music saved to {} ... Enjoy listening !".format(self.wavpath))



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

    def _get_fft_data(self, audio_seg, normed=False):
        audioslice = np.array(audio_seg.get_array_of_samples())
        num_samples = len(audioslice)
        fft_result = np.fft.fft(audioslice)[range(int(round(num_samples/2)) + 1)]
        step_size = audio_seg.frame_rate / num_samples
        bins = np.arange(0, int(round(num_samples/2)) + 1, 1.0) * step_size

        if normed:
            fft_result = np.abs(fft_result) / len(fft_result)
            bins = bins / 1000

        return bins, fft_result

    def _get_curve_data(self):
        current_x = 0
        xmins = []
        xmaxs = []
        curve = []

        for pitch, duration in self.song:
            curve.append(self.all_notes.index(pitch))
            xmins.append(current_x)
            current_x += (1./duration)
            xmaxs.append(current_x)

        return curve, xmins, xmaxs

    def compute_graph(self, show_graph, title=None):
        plt.figure(figsize=(6+4, 4+4))

        ### Curve plot
        ax = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        if title:
            plt.title(title)

        curve, xmins, xmaxs = self._get_curve_data()
        ax.hlines(curve, xmins, xmaxs, color='C0')

        ### Plot the base note
        ax.hlines([curve[0]], [0], [xmaxs[-1]], alpha=.5, color='C1')

        ### Add four lines above and below the curve
        min_y = max(0, min(curve) - 4)
        max_y = min(len(self.all_notes), max(curve) + 4)
        ax.set_yticks(np.arange(min_y, max_y))
        ax.set_ylim(min_y, max_y)
        ax.set_yticklabels(self.all_notes[min_y:max_y])
        ax.set_ylabel('Pitch')
        
        ax.set_xticks(())
        ax.set_xlabel('Duration')
        ax.grid(axis='y', color='gray', alpha=.2, linestyle='--')

        ### FFT Analysis
        ax = plt.subplot2grid((3, 1), (2, 0))

        harmony = audio.from_wav(self.wavpath)
        hist_bins, hist_vals = self._get_fft_data(harmony[1:3000], normed=True)
        ax.plot(hist_bins, hist_vals)

        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_xlabel("kHz")
        ax.set_ylabel("dB")

        plt.tight_layout()
        plt.savefig(self.wavpath[0:-3]+"png")
        if show_graph:
            plt.show()


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


class Beat(object):
    def __init__(self):
        super(Beat, self).__init__()

    @staticmethod
    def get_beat_list_by_emotions(emotion):
        emotion = emotion.lower()
        if emotion == "positive":
            pass
        elif emotion == "negative":
            pass
        elif emotion == "trust":
            pass
        elif emotion == "fear":
            pass
        elif emotion == "joy":
            pass
        elif emotion == "anticip":
            pass
        elif emotion == "sadness":
            pass
        elif emotion == "anger":
            pass
        elif emotion == "disgust":
            pass
        elif emotion == "surprise":
            pass

        return []

    @staticmethod
    def get_beat_test():
        res = {
            'length': 7*4 - 4,
            'rhythm':[
                ('snare_multiple', 0),
                # ('kick_kick7', 0),
                ('vocals_long_mod', 2),
                # ('kick_kick7', 2),
                # ('vocals_uhh', 4),
                # ('kick_kick7', 4),
                # ('kick_kick7', 6),
                # ('snare', 6),
                # ('kick_kick7', 8),
                # ('kick_kick7', 10),
                # ('snare', 10),
                # ('kick_kick7', 12),
                # ('snare', 14),
            ]
        }
        return res
    @staticmethod
    def get_beat_simple():
        res = {
            'length': 4,
            'rhythm': [('drum_kick', 0), ('drum_kick', 1), ('snare', 2)]
        }
        return res

    @staticmethod
    def get_beat_simple2():
        res = {
                'length': 4,
                'rhythm': [('drum_kick', 0), ('drum_kick', 2), ('snare', 0), ('snare', 1), ('snare', 3)]
            }
        return res

    @staticmethod
    def get_beat_rap():
        res = {
                'length': 16,
                'rhythm': [
                    ('drum_kick', 0), ('drum_kick', 1), ('snare', 2), ('drum_kick', 3), ('drum_kick', 4),
                    ('drum_kick', 5), ('snare', 6), ('drum_kick', 8), ('drum_kick', 9), ('snare', 10),
                    ('drum_kick', 11), ('drum_kick', 12), ('drum_kick', 13.6), ('snare', 14) 
                ]
            }
        return res

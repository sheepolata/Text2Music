import math
#sudo apt-get install python-pyaudio
from pyaudio import PyAudio
import sys
import numpy as np

import notesfreqs as nf

class SoundHandlerFrequences(object):
    """docstring for SoundHandlerFrequences"""
    def __init__(self):
        super(SoundHandlerFrequences, self).__init__()
        #See http://en.wikipedia.org/wiki/Bit_rate#Audio
        self.bitrate = 128000 #number of frames per second/frameset.

        self.pyaudio = PyAudio()
        self.stream = self.pyaudio.open(
            format=self.pyaudio.get_format_from_width(1),
            channels=1,
            rate=self.bitrate,
            output=True,
            )

    def __exit__(self):
        self.stream.close()
        self.pyaudio.terminate()


    def play_from_values(self, values, length, to_display):

        if len(values) != len(length) and len(values) != len(to_display) and len(length) != len(to_display):
            print("ERROR, all arguments must be of the same size")
            return

        freqs     = []
        durations = []

        index_min = 0
        index_max = len(nf.list_note2freqs) - 1

        values_min = min(values)
        values_max = max(values)

        for i in range(len(values)):
            freqs.append( math.floor((values[i] - values_min)/(values_max - values_min) * index_max) )
            durations.append( round(length[i] * 0.05, 2) )

        durations = self.randomise_duration_delta(durations)

        # print(freqs)
        # print(durations)

        last_display = ""
        for note in range(len(freqs)):
            disp = ">> " + nf.dict_freqs2notes[nf.list_note2freqs[freqs[note]]] + " - " + str(round((float(note)/(float(len(freqs))))*100, 2)) + "% (" + to_display[note] + ")"
            #Flush the last line
            sys.stdout.write(' ' * len(last_display) + '\r')
            #Write to display the current line
            sys.stdout.write("{0}\r".format(disp))

            last_display = disp

            self.play_tune(nf.list_note2freqs[freqs[note]], durations[note])

        sys.stdout.write("{0}\r".format('\n'))
        print("THE END")


    def play_tune(self, freq, length):
        NUMBEROFFRAMES = int(self.bitrate * length)
        RESTFRAMES = NUMBEROFFRAMES % self.bitrate
        WAVEDATA = ''

        for x in range(NUMBEROFFRAMES):
           WAVEDATA += chr(int(math.sin(x / ((self.bitrate / freq) / math.pi)) * 127 + 128))    

        #fill remainder of frameset with silence
        for x in range(RESTFRAMES): 
            WAVEDATA += chr(128)

        self.stream.write(WAVEDATA)

    def randomise_duration_delta(self, duration, initial_factor=1.0, delta=0.025, min_duration=0.4, max_duration=1.5, change_frequency=10, weigths=[0.2, 0.5, 0.3]):
        new_duration = []
        factor = initial_factor

        #mode : 0 (no change), -1 (decelerate), 1 (accelerate)
        mode = 0

        for i in range(len(duration)):
            # print (factor)
            if i%change_frequency == 0:
                mode = np.random.choice([-1, 0, 1], p=weigths)

            if mode == 0:
                factor = factor #No change
            elif mode == 1:
                factor = max(factor * (1-delta), min_duration) #accelerate
            elif mode == -1:
                factor = min(factor * (1+delta), max_duration) #decelerate

            new_duration.append(duration[i] * factor)

        return new_duration
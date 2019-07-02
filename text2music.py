import file
import sys
from os import path

from pysynth import SoundPySynth

def text_2_music(filepath, bpm, instrument, gen, octave):
    print("###### Welcome to the TextToMusic Program V2 ######")
    filename = path.splitext(filepath)[0]
    filepath = "./data/" + filepath
    f = file.TextFileToMusic(filepath)
    output_file = "./output/" + filename + "_"
    s = SoundPySynth(octave=int(octave), bpm=int(bpm), generation_type=gen)


    song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel", version=instrument)

    '''
    Join wav files together (one after the other)
    '''
    # sound1 = pydub.AudioSegment.from_wav("1_b_mean.wav")
    # sound2 = pydub.AudioSegment.from_wav("1_p_mean.wav")
    # sound3 = pydub.AudioSegment.from_wav("1_s_mean.wav")
    # combined_sounds = sound1 + sound2 + sound3 
    # combined_sounds.export("joinedFile.wav", format="wav")

if __name__ == '__main__':

    # Tuples are the arguments of the software
    # 1: argument name
    # 2: default value
    # 3: message displayed to help the user
    args = [
        (
            'b',
            180,
            'The music bpm',
        ),
        (
            'i',
            'a',
            'The instrument type: a|b|c|d|e|p|s'
        ),
        (
            'g',
            'chain',
            'The type of generator: chain|base'
        ),
        (
            'o',
            4,
            'The base octave: [2:6]'
        ),

    ]

    if len(sys.argv) == 1 or '-help' in sys.argv or '-h' in sys.argv:
        print('Usage: {} filename [options]'.format(sys.argv[0]))
        print('\nThe filename is the text that you want to convert into music')
        print('options list:')
        for name_, default_value, help_message in args:
            print('    -{}\t{} (default:{})'.format(name_, help_message, default_value))

        print()
    else:
        option_values = {}
        for name_, default_value, help_message in args:
            try:
                id_name = sys.argv.index('-{}'.format(name_)) + 1
                option_values[name_] = sys.argv[id_name]
            except:
                option_values[name_] = default_value

        text_2_music(sys.argv[1], **option_values)

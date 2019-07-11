import file
import sys
from os import path

from pysynth import SoundPySynth

def text_2_music(filepath, octave, generator, markov, plotmusic, **params):
    print("###### Welcome to the TextToMusic Program V2 ######")
    filename = path.splitext(filepath)[0]
    filepath = "./data/" + filepath
    f = file.TextFileToMusic(filepath, filename)

    # Get a few parameters that are derived from the title
    bpm, instrument = f.get_params(**params)

    output_file = "./output/" + filename
    s = SoundPySynth(octave=octave, bpm=bpm, generation_type=generator)

    # song = s.generate_wav(f.get_words_values(f="mean"), f.get_duration_factors(f="len"), filepath=output_file+"channel", version=instrument, markov=markov)
    # song = s.generate_wav(f, filepath=output_file, version=instrument, markov=markov)
    song = s.generate_orchestra(f, filepath=output_file, version=instrument, markov=markov)
    if plotmusic:
        s.show_graph(filename)


    # s.playWavWithDispay()

    '''
    Join wav files together (one after the other)
    '''
    # sound1 = pydub.AudioSegment.from_wav("1_b_mean.wav")
    # sound2 = pydub.AudioSegment.from_wav("1_p_mean.wav")
    # sound3 = pydub.AudioSegment.from_wav("1_s_mean.wav")
    # combined_sounds = sound1 + sound2 + sound3 #Check OVERLAY
    # combined_sounds.export("joinedFile.wav", format="wav")

if __name__ == '__main__':

    # Tuples are the arguments of the software
    # 1: argument sign
    # 1: argument fullname
    # 2: default value
    # 3: message displayed to help the user
    args = [
        (
            'b',
            'bpm',
            -1,
            'The music bpm, auto-selected if \"-1\"',
            False
        ),
        (
            'i',
            'instrument',
            'none',
            'The instrument type: a|b|c|d|e|p|s, auto-selected if \"none\"',
            False
        ),
        (
            'g',
            'generator',
            'chain',
            'The type of generator: chain|base',
            False
        ),
        (
            'o',
            'octave',
            4,
            'The base octave: [2:6]',
            False
        ),
        (
            'm',
            'markov',
            False,
            'Read the input file, construct a markov chain and use this markiv chain to generate the text from which the song will be created',
            True
        ),
        (
            'mlen',
            'markovgenerationlength',
            100,
            'Set the number of word to be generated by the markov chain',
            False
        ),
        (
            'ms',
            'markovseed',
            -1,
            'Set the random seed for the markov generation process',
            False
        ),
        (
            'rlm',
            'reloadmarkov',
            False,
            'Force the recomputing of the markov chain',
            True
        ),
        (
            'p',
            'plotmusic',
            False,
            'Plot the music',
            True
        )
    ]

    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print('Usage: {} filename [options]'.format(sys.argv[0]))
        print('\nThe filename contains the text that you want to convert into music')
        print('If no arguments are given, the title will be used to derive them')
        print('options list:')
        for name_, _, default_value, help_message, no_value in args:
            print('    -{}\t{} (default:{})'.format(name_, help_message, default_value))

        print()
    else:
        option_values = {}
        # option_values['usetitle'] = len(sys.argv) == 2
        
        for name_, fullname, default_value, help_message, no_value in args:
            try:
                if not no_value:
                    id_name = sys.argv.index('-{}'.format(name_)) + 1
                    param_value = sys.argv[id_name]
                    if param_value.isdigit():
                        param_value = int(param_value)
                    elif param_value == 'True':
                        param_value = True
                    elif param_value == 'False':
                        param_value = False

                    option_values[fullname] = param_value
                else:
                    id_name = sys.argv.index('-{}'.format(name_))
                    option_values[fullname] = not default_value
            except:
                option_values[fullname] = default_value

        text_2_music(sys.argv[1], **option_values)

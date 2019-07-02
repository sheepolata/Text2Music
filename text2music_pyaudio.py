
import file
import sound
import notesfreqs

def main():

    print("###### Welcome to the TextToMusic Program ######")

    default_file = "./data/3mt.txt"
    f = file.TextFileToMusic(default_file)
    s = sound.SoundHandlerFrequences()
    
    print("Playing ===> " + default_file + "...")

    s.play_from_values(f.get_words_values(), f.get_words_length(), f.words)

if __name__ == '__main__':
    main()
import string
import operator
import numpy as np
import json as js
from pprint import pprint

class TextFileToMusic(object):
    """docstring for TextFileToMusic"""
    def __init__(self, path, title):
        super(TextFileToMusic, self).__init__()
        self.path = path
        self.content = ""
        self.title = title.lower()

        self.file = open(self.path, "r", encoding="utf8")

        self.raw_content = self.file.read()

        #Remove ponctuation
        exclude = set(string.punctuation)
        self.content = ''.join(ch for ch in self.content if ch not in exclude)
        self.content = self.content.lower()

        self.words = self.content.split()

        self.markov = {}

    def computeMarkovChain(self):

        try:
            with open("./data/markovchains/" + self.title + "_markovchain.json", 'r') as fp:
                print("Load Markov Chain from " + "./data/markovchains/" + self.title + "_markovchain.json\r", end='', flush=True)
                self.markov = js.load(fp)
                print("Load Markov Chain from " + "./data/markovchains/" + self.title + "_markovchain.json - done\r", end='', flush=True)
                print('')
        except:
            raw_words = self.raw_content.split()
            # print(self.raw_content)
            # print(raw_words)

            ponct_after  = ['.',',','?','!',':',';',']','}','\''] #['.',',','?','!',':',';',')',']','}']
            ponct_before = ['{','[','('] #['(','[','{']

            j = 0.0
            for w in raw_words:
                print("Fixing Raw content... {0}%\r".format(round(((j/float(len(raw_words)))*100.0), 2)), end='', flush=True)
                j += 1.0
                # if any((c in ponct_after) for c in w) and len(w) > 1:
                if any((c in w) for c in ponct_before) and len(w) > 1:
                    if w[0] not in ponct_before:
                        continue
                    i = raw_words.index(w)
                    del raw_words[i]
                    raw_words.insert(i, w[0])
                    raw_words.insert(i+1, w[1:])
                # elif any((c in ponct_before) for c in w) and len(w) > 1:
                elif any((c in w) for c in ponct_after) and len(w) > 1:
                    if w[-1] not in ponct_after:
                        continue
                    i = raw_words.index(w)
                    del raw_words[i]
                    raw_words.insert(i, w[:-1])
                    raw_words.insert(i+1, w[-1])
            print("Fixing Raw content... {0}% - done\r".format(round(((j/float(len(raw_words)))*100.0), 2)), end='', flush=True)
            print('')

            # print(raw_words)

            for index in range(len(raw_words)-1):
                print("Contructing Markov chain... {0}%\r".format(round((float(index)/float(len(raw_words)))*100.0, 2)), end='', flush=True)

                _current = raw_words[index]
                _next = raw_words[index+1]

                if _current not in self.markov:
                    self.markov[_current] = {}

                if _next not in self.markov[_current]:
                    self.markov[_current][_next] = 1
                else:
                    self.markov[_current][_next] += 1
            
            print("Contructing Markov chain... {0}% - done\r".format(round((float(index+2)/float(len(raw_words)))*100.0, 2)), end='', flush=True)
            print('')

            with open("./data/markovchains/" + self.title + "_markovchain.json", 'w') as fp:
                print("Write Markov Chain to " + "./data/markovchains/" + self.title + "_markovchain.json\r", end='', flush=True)
                js.dump(self.markov, fp, sort_keys=True, indent=4)
                print("Write Markov Chain to " + "./data/markovchains/" + self.title + "_markovchain.json - done\r", end='', flush=True)
                print('')

            # pprint(self.markov)

    def generateTextFromMarkov(self, length=500):
        gen_txt = []

        first = np.random.choice(list(self.markov.keys()))
        gen_txt.append(first)
        # print(first)

        prev = first
        for i in range(length):
            print("Generating text... {0}%\r".format(round((float(i)/float(length))*100.0, 2)), end='', flush=True)

            choices = list(self.markov[prev].keys())
            p = list(self.markov[prev].values())
            _s = np.sum(p)
            p /= _s

            choice = np.random.choice(choices, p=p)
            gen_txt.append(choice)
            prev = choice

        print("Generating text... {0}% - done\r".format(round((float(i+1)/float(length))*100.0, 2)), end='', flush=True)
        print('')

        ponct_after  = ['.',',','?','!',':',';',')',']','}']
        ponct_before = ['(','[','{']
        lres = []
        res = ""
        j = 0.0
        for w in gen_txt:
            print("Fix generated text... {0}%\r".format(round((float(j)/float(len(gen_txt)))*100.0, 2)), end='', flush=True)
            j += 1.0
            if w in ponct_before:
                    res += w
            if w in ponct_after:
                res = res[:-1]
                if w == '.':
                    # res += w + '\n'
                    lres.append(res + w)
                    res = ""
                else:
                    res += w + " "
            else:
                res += w + " "
        print("Fix generated text... {0}% - done\r".format(round((float(j)/float(len(gen_txt)))*100.0, 2)), end='', flush=True)
        print('')
        # print(lres)

        return lres


    def get_word_value(self, word, f="mean"):
        if f == "mean":
            return self.mean(word)
        elif f == "addition":
            return self.addition(word)
        elif f == "len":
            return len(word)
        else :
            return self.mean(word)

    def mean(self, word):
        #Mean character value
        _sum = 0
        for c in word:
            _sum += ord(c)
        return int(_sum/len(word))

    def addition(self, word):
        res = ord(word[0])
        for c in range(len(word)-1):
            res += ord(word[c])
        return res

    def get_words_values(self, f="mean"):
        res = []
        for w in self.words:
            res.append(self.get_word_value(w, f))
        return res

    def get_duration_factors(self, f="len"):
        if f == "len":
            return self.get_words_length()
        elif f == "addition":
            return self.get_words_values(f=f)
        elif f == "mean":
            return self.get_words_values(f=f)
        else:
            return self.get_words_length()

    def get_words_length(self):
        res = []
        for w in self.words:
            res.append(len(w))
        return res

    def _get_instrument(self):
        # instrument = 's'

        # if 'a' in self.title:
        #     instrument = 'a'
        # elif 'b' in self.title:
        #     instrument = 'b'
        # elif 'c' in self.title:
        #     instrument = 'c'
        # elif 'd' in self.title:
        #     instrument = 'd'
        # elif 'e' in self.title:
        #     instrument = 'e'
        # elif 'p' in self.title:
        #     instrument = 'p'

        instruments = ['a', 'b', 'e', 's']
        d = {'a' : 0, 'b' : 0, 'e' : 0, 's' : 0}
        for c in self.title:
            if c in instruments:
                d[c] += 1
            else:
                _diff = []
                for i in instruments:
                    _diff.append(abs(ord(i) - ord(c)))
                d[instruments[_diff.index(min(_diff))]] += 1
        
        m = max(d.items(), key=operator.itemgetter(1))[0]

        if d[m] == 0:
            return np.random.choice(instruments)
        else:
            return m
        
        # return instrument
    
    def _get_bpm(self):
        # candidates = [120, 150, 180, 210, 240]
        bpm_range = [140, 240]

        #Split into words
        title_words = self.title.split()

        if len(title_words) <= 1:
            return np.mean(bpm_range)

        #Get word mean values
        title_words_values = [self.addition(x) for x in title_words]
        #Select a random value from title_words_values, seeded by the sum of the word values so the chosen value stays the same for each run
        np.random.seed(np.sum(title_words_values))
        _value = np.random.choice(title_words_values)
        np.random.seed(None)

        #Normalise the value and select a bmp accordingly
        norm = (((_value - min(title_words_values))/(max(title_words_values) - min(title_words_values))))
        _bpm = int(bpm_range[0] + norm*(bpm_range[1] - bpm_range[0]))

        return _bpm

        # v = 0
        # chance = .5
        # for c in self.title:
        #     v += ord(c)/2
        #     if v > bpm_range[1]:
        #         v = bpm_range[1]
        #         break
        #     if v > bpm_range[0]:
        #         if np.random.random() > chance:
        #             break
        #         else:
        #             chance *= .9

        # return int(v)
        # return candidates[len(self.title) % len(candidates)]

    def get_params(self, bpm, instrument, generator, octave, usetitle):
        if usetitle == True:
            return self._get_bpm(), self._get_instrument(), generator, int(octave)
        else:
            return int(bpm), instrument, generator, int(octave)


if __name__ == '__main__':
    # f = TextFileToMusic("./data/The Bible.txt", "The Bible")
    f = TextFileToMusic("./data/The Bible Small.txt", "The Bible Small")

    f.computeMarkovChain()
    t = f.generateTextFromMarkov(length = 1000)

    r = open("./output/markov_" + f.title + ".txt", "w", encoding='utf-8')
    disp_i = 0
    for i, l in enumerate(t):
        disp_i = i
        print("Write text... {0}%\r".format(round((float(i)/float(len(t)))*100.0, 2)), end='', flush=True)
        r.write(l + '\n')
    print("Write text... {0}% - done\r".format(round((float(disp_i+1)/float(len(t)))*100.0, 2)), end='', flush=True)
    print('')
    print("Results wrote to" + "./output/markov_" + f.title + ".txt")

    r.close()
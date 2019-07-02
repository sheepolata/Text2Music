import string
import operator
import numpy as np

class TextFileToMusic(object):
    """docstring for TextFileToMusic"""
    def __init__(self, path, title):
        super(TextFileToMusic, self).__init__()
        self.path = path
        self.content = ""
        self.title = title.lower()

        self.file = open(self.path, "r", encoding="utf8")

        self.content = self.file.read()

        #Remove ponctuation
        exclude = set(string.punctuation)
        self.content = ''.join(ch for ch in self.content if ch not in exclude)
        self.content = self.content.lower()

        self.words = self.content.split()

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

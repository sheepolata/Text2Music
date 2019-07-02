import string

class TextFileToMusic(object):
    """docstring for TextFileToMusic"""
    def __init__(self, path):
        super(TextFileToMusic, self).__init__()
        self.path = path
        self.content = ""

        self.file = open(self.path, "r", encoding="utf8")

        self.content = self.file.read()

        #Remove ponctuation
        exclude = set(string.punctuation)
        self.content = ''.join(ch for ch in self.content if ch not in exclude)
        
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

import string
import operator
import numpy as np
import json as js
from pprint import pprint
import spacy, threading, time
import collections
import myglobals

class TextFileToMusic(object):
    """docstring for TextFileToMusic"""
    def __init__(self, path, title):
        super(TextFileToMusic, self).__init__()
        self.path = path
        self.content = ""
        self.title = title.lower()

        self.file = open(self.path, "r", encoding="utf8")

        self.raw_content = self.file.read()

        self.spacy_model = "en_core_web_lg"
        # self.spacy_model = "en_vectors_web_lg"

        self.recorded_emotions = ["anger", "anticip", "disgust", "fear", "joy", "negative", "positive", "sadness", "surprise", "trust"]
        
        def load_disp(text):
            load = ['\\', '|', '/', '-']
            i = 0
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                print("{} {}\r".format(text, load[i]), end='', flush=True)
                i = (i+1)%len(load)
                time.sleep(0.15)

        if not myglobals.RUN_GUI:
            t = threading.Thread(target=load_disp, args=("Loading Spacy Model {}...".format(self.spacy_model),))
            t.start()
            self.nlp = spacy.load(self.spacy_model)
            t.do_run = False
            t.join()
        else:
            print("Loading Spacy Model {}...\r".format(self.spacy_model), end='', flush=True)
            self.nlp = spacy.load(self.spacy_model)
        print("Loading Spacy Model {}... done\r".format(self.spacy_model), end='', flush=True)
        print('')

        # self.nlp.max_length = 4500000

        default_lexicon = "./data/Emoxicon/NRC-Sentiment-Emotion-Lexicons/NRC-Emotion-Lexicon-v0.92/NRC-Emotion-Lexicon-Senselevel-v0.92.txt"

        if not myglobals.RUN_GUI:
            t = threading.Thread(target=load_disp, args=("Loading Lexicon {}...".format(default_lexicon),))
            t.start()
            self.emoxicon = self.loadEmoxicon(default_lexicon)
            t.do_run = False
            t.join()
        else:
            print("Loading Lexicon {}...\r".format(default_lexicon), end='', flush=True)
            self.emoxicon = self.loadEmoxicon(default_lexicon)
        print("Loading Lexicon {}... done\r".format(default_lexicon), end='', flush=True)
        print('')

        def token_emotion_getter(token):
            if token.text.lower() in self.emoxicon.keys():
                return self.emoxicon[token.text.lower()]
            else:
                return None
                # return {"anger": 0,
                #         "anticip": 0,
                #         "disgust": 0,
                #         "fear": 0,
                #         "joy": 0,             
                #         "negative": 0,
                #         "positive": 0,
                #         "sadness": 0,
                #         "surprise": 0,
                #         "trust": 0,
                #         "synonym": []}

        def docspan_emotion_getter(obj):
            res = {}
            for t in obj:
                em = t._.emotions
                if em != None:
                    for k in em.keys():
                        if k != "synonym":
                            if k in res.keys():
                                res[k] += em[k]
                            else:
                                res[k] = em[k]
            if not res:
                return None
            else:
                _sum = 0
                for k in res:
                    _sum += res[k]
                if _sum <= 0:
                    return res
                for k in res:
                    res[k] = round(res[k]/_sum, 4)
                return res
                    

        if not myglobals.RUN_GUI:
            t = threading.Thread(target=load_disp, args=("Set Spacy emotion extension ...",))
            t.start()
        else:
            print("Set Spacy emotion extension ...\r", end='', flush=True)

        try:
            spacy.tokens.Token.set_extension("emotions")
        except KeyError:
            spacy.tokens.Token.set_extension("emotions", getter=token_emotion_getter)
            
        try:
            spacy.tokens.Doc.set_extension("emotions")
        except KeyError:
            spacy.tokens.Doc.set_extension("emotions", getter=docspan_emotion_getter)

        try:
            spacy.tokens.Span.set_extension("emotions")
        except KeyError:
            spacy.tokens.Span.set_extension("emotions", getter=docspan_emotion_getter)

        lim = 1000000
        if len(self.raw_content) > lim:
            rnd = np.random.randint(0, len(self.raw_content)-lim-1)
            raw_content_limited = self.raw_content[rnd:rnd+lim]
        else:
            raw_content_limited = self.raw_content
        # print(raw_content_limited)

        self.content = self.nlp(raw_content_limited)

        #Remove ponctuation
        # exclude = set(string.punctuation)
        # self.content = ''.join(ch for ch in self.raw_content if ch not in exclude)
        # self.content = self.content.lower()

        self.words = []
        self.tokens = []
        for tok in self.content:
            if tok.pos_ not in ["SPACE", "PUNCT"]:
                self.words.append(tok.text)
                self.tokens.append(tok)
                # print(tok.text, tok.pos_)
        
        if not myglobals.RUN_GUI:
            t.do_run = False
            t.join()

        print("Set Spacy emotion extension ... done\r", end='', flush=True)
        print('')

        # for sent in self.content.sents:
        #     print(sent.text, sent._.emotions)

        # print(self.content._.emotions)

        doc_emotions           = self.content._.emotions
        self.most_repr_emotion = max(doc_emotions.items(), key=operator.itemgetter(1))[0]
        self.second_most_repr_emotion = [k for k,v in sorted(doc_emotions.items(), key=lambda item: item[1], reverse=True)][1]
        em_max_val             = max(doc_emotions.items(), key=operator.itemgetter(1))[1]

        print("\nMost represented emotion in \"{}\" : {} ({}%)".format(self.title, self.most_repr_emotion.upper(), round(em_max_val*100, 2)))
        print("Emotions represented, by order of importance:")
        max_len = max([len(x) for x in doc_emotions.keys()])
        sorted_x = sorted(doc_emotions.items(), key=operator.itemgetter(1), reverse=True)
        sorted_dict = collections.OrderedDict(sorted_x)
        for k in sorted_dict:
            space = ""
            for i in range(0, max_len-len(k)):
                space += " "
            print("\t{}  at  {}%".format(k.upper()+space, round(sorted_dict[k]*100, 2)))
        print('\n')

        # for chunck in self.content.noun_chunks:
        #     print(chunck)

        self.markov = {}

        self.ponct_after  = ['.',',','?','!',':',';',']','}','\''] #['.',',','?','!',':',';',')',']','}']
        self.ponct_before = ['{','[','('] #['(','[','{']

        self.markov_seed = -1

    def loadEmoxicon(self, filepath):
        lex = open(filepath, 'r')

        res = {}

        for line in lex.readlines():
            elements = line.split("\t")

            word    = elements[0].split("--")[0]
            syn     = elements[0].split("--")[1].split(",")
            emotion = elements[1]
            value   = int(elements[2])

            if word in res.keys():
                if emotion in res[word].keys():
                    continue
                else:
                    res[word][emotion]   = value
            else:
                res[word] = {}
                res[word]["synonym"] = syn
                res[word][emotion]   = value

        lex.close()
        return res

    def computeMarkovChain(self):
        try:
            if self.reloadmarkov:
                raise Exception('Reload Markov forced') 
            with open("./data/markovchains/" + self.title + "_markovchain.json", 'r') as fp:
                print("Load Markov Chain from " + "./data/markovchains/" + self.title + "_markovchain.json\r", end='', flush=True)
                self.markov = js.load(fp)
                print("Load Markov Chain from " + "./data/markovchains/" + self.title + "_markovchain.json - done\r", end='', flush=True)
                print('')
        except:
            raw_words = self.raw_content.split()
            # print(self.raw_content)
            # print(raw_words)

            

            j = 0.0
            for w in raw_words:
                print("Fixing Raw content... {0}%\r".format(round(((j/float(len(raw_words)))*100.0), 2)), end='', flush=True)
                j += 1.0
                # if any((c in ponct_after) for c in w) and len(w) > 1:
                if any((c in w) for c in self.ponct_before) and len(w) > 1:
                    if w[0] not in self.ponct_before:
                        continue
                    i = raw_words.index(w)
                    del raw_words[i]
                    raw_words.insert(i, w[0])
                    raw_words.insert(i+1, w[1:])
                # elif any((c in ponct_before) for c in w) and len(w) > 1:
                elif any((c in w) for c in self.ponct_after) and len(w) > 1:
                    if w[-1] not in self.ponct_after:
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

    def generateTextFromMarkov(self, length=100):
        self.computeMarkovChain()

        if self.markov_seed < 0:
            import time
            self.markov_seed = int(time.time())

        np.random.seed(self.markov_seed)

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

        lres = []
        res = ""
        j = 0.0
        for w in gen_txt:
            print("Fix generated text... {0}%\r".format(round((float(j)/float(len(gen_txt)))*100.0, 2)), end='', flush=True)
            j += 1.0
            if w in self.ponct_before:
                    res += w
            if w in self.ponct_after:
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

        np.random.seed(None)

        return lres

    def wordListFromMarkov(self, length=100):
        line_list = self.generateTextFromMarkov(length)
        
        as_string = ""
        wlist = []

        for i, line in enumerate(line_list):
            as_string += line + " "
            
        #Remove ponctuation
        exclude = set(string.punctuation)
        as_string = ''.join(ch for ch in as_string if ch not in exclude)
        as_string = as_string.lower()

        return (as_string.split(), line_list)


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

    def get_words_values(self, f="mean", words=[]):
        if words == []:
            words = self.words
        res = []
        if f == "spacy":
            spacy_words = ""
            for w in words:
                spacy_words += w + " "
            toks = self.nlp(spacy_words)
            for i in range(0, len(toks)-1):
                tok      = toks[i]
                next_tok = toks[i+1]
                if tok.has_vector and next_tok.has_vector:
                    # res.append(tok.similarity(next_tok))
                    v = tok.similarity(next_tok)
                    # print(tok.text, next_tok.text, tok.similarity(next_tok))
                else:
                    # res.append(0.0)
                    v = 0.0
                res.append([v, tok.pos_])

            if toks[-1].has_vector and toks[0].has_vector:
                # res.append(toks[-1].similarity(toks[0]))
                v = toks[-1].similarity(toks[0])
            else:
                # res.append(0.0)
                v = 0.0

            res.append([v, toks[-1].pos_])

            # print(self.tokens[-1].text, self.tokens[0].text, self.tokens[-1].similarity(self.tokens[0]))
        else:
            for w in words:
                res.append(self.get_word_value(w, f))
        return res

    def get_duration_factors(self, f="len", words=[]):
        if words == []:
            words = self.words
        if f == "len":
            return self.get_words_length(words)
        elif f == "addition":
            return self.get_words_values(f=f, words=words)
        elif f == "mean":
            return self.get_words_values(f=f, words=words)
        else:
            return self.get_words_length(words=words)

    def get_words_length(self, words):
        res = []
        for w in words:
            res.append(len(w))
        return res

    def _get_instrument(self):
        # print("Get instrument")

        # instruments = ['a', 'b', 'e', 's']
        # d = {'a' : 0, 'b' : 0, 'e' : 0, 's' : 0}
        # for c in self.title:
        #     if c in instruments:
        #         d[c] += 1
        #     else:
        #         _diff = []
        #         for i in instruments:
        #             _diff.append(abs(ord(i) - ord(c)))
        #         d[instruments[_diff.index(min(_diff))]] += 1
        
        # m = max(d.items(), key=operator.itemgetter(1))[0]

        # if d[m] == 0:
        #     return np.random.choice(instruments)
        # else:
        #     return m

        # ["anger", "anticip", "disgust", "fear", "joy", "negative", "positive", "sadness", "surprise", "trust"]

        if self.most_repr_emotion.lower() in ["joy", "positive", "trust"]:
            c = np.random.choice(['s', 'e'])
        elif self.most_repr_emotion.lower() in ["anticip", "surprise"]:
            c = np.random.choice(['a', 'e'])
        elif self.most_repr_emotion.lower() in ["disgust", "fear", "negative", "sadness", "anger"]:
            c = np.random.choice(['a', 'b'])
        print("Instrument chosen : \"{}\", based on the text most represented emotion ({})".format(c.upper(), self.most_repr_emotion.upper()))
        return c
        
        # return instrument

    def _get_octave(self):
        if self.second_most_repr_emotion.lower() in ["joy", "positive", "trust"]:
            o = 5
        elif self.second_most_repr_emotion.lower() in ["anticip", "surprise"]:
            o = 4
        elif self.second_most_repr_emotion.lower() in ["disgust", "fear", "negative", "sadness", "anger"]:
            o = 3
        print("Octave chosen : {}, based on the text second most represented emotion ({})".format(o, self.second_most_repr_emotion.upper()))
        return o
    
    def _get_bpm(self):
        if self.most_repr_emotion.lower() in ["joy", "anger"]:
            b = 240
        elif self.most_repr_emotion.lower() in ["positive", "trust"]:
            b = 160
        elif self.most_repr_emotion.lower() in ["anticip", "surprise"]:
            b = 200
        elif self.most_repr_emotion.lower() in ["negative", "sadness"]:
            b = 120
        elif self.most_repr_emotion.lower() in ["disgust", "fear"]:
            b = 220
        print("BPM chosen : {}, based on the text most represented emotion ({})".format(b, self.most_repr_emotion.upper()))
        return b

        ###############################################
        # bpm_range = [140, 240]

        # #Split into words
        # title_words = self.title.split()

        # if len(title_words) <= 1:
        #     return np.mean(bpm_range)

        # #Get word mean values
        # title_words_values = [self.addition(x) for x in title_words]
        # #Select a random value from title_words_values, seeded by the sum of the word values so the chosen value stays the same for each run
        # np.random.seed(np.sum(title_words_values))
        # _value = np.random.choice(title_words_values)
        # np.random.seed(None)

        # #Normalise the value and select a bmp accordingly
        # norm = (((_value - min(title_words_values))/(max(title_words_values) - min(title_words_values))))
        # _bpm = int(bpm_range[0] + norm*(bpm_range[1] - bpm_range[0]))

        # return _bpm

        ###############################################
        # candidates = [120, 150, 180, 210, 240]
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

    def get_params(self, bpm, instrument, octave, markovgenerationlength, markovseed, reloadmarkov, **_):
        self.markov_seed = markovseed
        self.reloadmarkov = reloadmarkov
        self.markov_length = markovgenerationlength
        _bpm   = self._get_bpm() if bpm == -1 else bpm
        _instr = self._get_instrument() if instrument == "none" else instrument
        _octave = self._get_octave() if octave == -1 else octave
        print('\n')
        return _bpm, _instr, _octave

        # if usetitle == True:
        #     return self._get_bpm(), self._get_instrument()
        # else:
        #     return bpm, instrument


if __name__ == '__main__':
    # f = TextFileToMusic("./data/The Bible.txt", "The Bible")
    f = TextFileToMusic("./data/The Bible.txt", "The Bible")

    # f.computeMarkovChain()
    # t = f.generateTextFromMarkov(length = 1000)

    # r = open("./output/markov_" + f.title + ".txt", "w", encoding='utf-8')
    # disp_i = 0
    # for i, l in enumerate(t):
    #     disp_i = i
    #     print("Write text... {0}%\r".format(round((float(i)/float(len(t)))*100.0, 2)), end='', flush=True)
    #     r.write(l + '\n')
    # print("Write text... {0}% - done\r".format(round((float(disp_i+1)/float(len(t)))*100.0, 2)), end='', flush=True)
    # print('')
    # print("Results wrote to" + "./output/markov_" + f.title + ".txt")
    # r.close()

    # pprint(f.content._.emotions)


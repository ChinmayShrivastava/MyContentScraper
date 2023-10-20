import networkx as nx
import pickle
import nltk

class SEOStats:

    def __init__(self, articlepath, graphpath):
        
        # article is a string
        # read article from file
        with open(articlepath, 'r') as articlefile:
            self.article = articlefile.read().lower()
        self.G = pickle.load(open('graph.pickle', "rb"))
        self.kws = {}
        self.wordcount = 0
        self.addkws = []

    # make ngam
    def make_ngrams(self, text, n):
        tokens = nltk.word_tokenize(text)
        ngrams = nltk.ngrams(tokens, n)
        return [ ' '.join(grams) for grams in ngrams]
    
    def add_additional_kw(self, kw):
        self.addkws.append(kw)
    
    def findkws(self):
        # for ngrams in article find if they are in the graph
        # if they are, add them to the kws dict
        for n in range(1, 5):
            ngrams = self.make_ngrams(self.article, n)
            for ngram in ngrams:
                if ngram in self.G.nodes():
                    self.kws[ngram] = {}
        # add additional keywords
        for kw in self.addkws:
            self.kws[kw] = {}
    
    def calcWordCount(self):
        words = self.article.split(' ')
        self.wordcount = len(words)

    def calcKWCount(self):
        # for kw in kws, find the number of times it appears in the article
        for kw in self.kws:
            self.kws[kw]['count'] = self.article.count(kw)

    def calculateKWdensity(self):
        # for kw in kws, find the number of times it appears in the article
        # divide by wordcount
        for kw in self.kws:
            self.kws[kw]['density'] = self.kws[kw]['count']/self.wordcount

    def calculateKWfrequency(self):
        # for kw in kws, find the number of times it appears in the article
        # divide by wordcount
        for kw in self.kws:
            self.kws[kw]['frequency'] = self.kws[kw]['count']/self.wordcount

    def visualise_kws(self):
        # print kws in order of density, and print density
        print("Density of keywords:")
        for kw in sorted(self.kws, key=lambda x: self.kws[x]['density'], reverse=True):
            print(kw, self.kws[kw]['density']*100)

    def statpipeline(self):
        self.findkws()
        self.calcWordCount()
        self.calcKWCount()
        self.calculateKWdensity()
        self.calculateKWfrequency()
        self.visualise_kws()

    def getKWstats(self, kw):
        return self.kws[kw]
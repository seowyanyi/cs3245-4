#!/usr/bin/python

try:
   import cPickle as pickle
except:
   import pickle


class InvertedIndex:
    def __init__(self, dictionary_file, postings_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        f = open(dictionary_file, 'r')        
        self.dictionary = Dictionary(pickle.loads(f.read()))
        f.close()

    def get_dictionary(self):
        return self.dictionary 

    def get_postings_list(self, term):
        dictionary_term = self.dictionary.get_term(term)
        if not dictionary_term:
            return None
        f = open(self.postings_file, 'r')
        f.seek(dictionary_term['pointer'])
        data_string = f.read(dictionary_term['bytes'])
        f.close()
        return pickle.loads(data_string)

class Dictionary:
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def get_term(self, term):
        try:
            return self.dictionary[term]
        except KeyError:
            return None

    def get_pointer(self, term):
        t = self.get_term(term)
        if not t:
            return None
        return t['pointer']

    def get_bytes(self, term):
        t = self.get_term(term)
        if not t:
            return None
        return t['bytes']        

    def get_frequency(self, term):
        t = self.get_term(term)
        if not t:
            return None
        return t['frequency']                
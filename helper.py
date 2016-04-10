#!/usr/bin/python
import nltk
from nltk.stem.porter import PorterStemmer
import re

def remove_stop_words(tokens):
    """
    Params:
    @tokens: Normalized set of tokens

    In query descriptions, there are often introductory words like
    'Relevant documents will describe' which does nothing to describe the document.
    Patent documents also have common stopwords which are removed here.
    source: http://www.uspto.gov/patft//help/stopword.htm
    We remove these along with stop words in the NLTK library. 
    """
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(['relevant', 'documents', 'document', 'will', 'describe', 'accordance', 
        'according', 'another', 'claim', 'comprises', 'corresponding', 'could', 'desired', 
        'embodiment', 'figs', 'fig', 'further', 'generally', 'herein', 'invention', 'particularly',
        'preferably', 'preferred', 'present', 'provide', 'relatively', 'respectively', 'said',
        'should', 'since', 'some', 'such', 'suitable', 'thereby', 'therefore', 'thereof', 'thereto',
        'various', 'wherein', 'which', 'mechanisms' ,'other'])
    stopwords = normalize_tokens(stopwords)
    return [w for w in tokens if w.lower() not in stopwords]

def filter_invalid_characters(tokens):
    """
    Filters out invalid characters like punctuation. Here we only whitelist
    alphabets and '-', rationale being only words and not numbers are descriptive of
    what a patent is about. This reduces the noise in the data. 
    """
    pattern = re.compile('^[a-zA-Z\-]+$')
    return filter(lambda x: pattern.match(x), tokens)

def stemmer(tokens):
    """
    Applies stemming to a given array of tokens
    """
    porter_stemmer = PorterStemmer()
    return [porter_stemmer.stem(token) for token in tokens]

def case_folder(tokens):
    """
    Converts all tokens to lower case
    """
    return [token.lower() for token in tokens]    

def normalize_tokens(tokens):
    tokens = stemmer(tokens)
    return case_folder(tokens)

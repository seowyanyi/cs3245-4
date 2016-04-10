#!/usr/bin/python
import nltk
from nltk.stem.porter import PorterStemmer
import re
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError

PATENT_STOPWORDS = ['relevant', 'documents', 'document', 'will', 'describe', 'accordance', 
    'according', 'another', 'claim', 'comprises', 'corresponding', 'could', 'desired', 
    'embodiment', 'figs', 'fig', 'further', 'generally', 'herein', 'invention', 'particularly',
    'preferably', 'preferred', 'present', 'provide', 'relatively', 'respectively', 'said',
    'should', 'since', 'some', 'such', 'suitable', 'thereby', 'therefore', 'thereof', 'thereto',
    'various', 'wherein', 'which', 'other', 'using', 'means', 'include', 'technology',
    'technologies']

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
    stopwords.extend(PATENT_STOPWORDS)
    stopwords = normalize_tokens(stopwords)
    return [w for w in tokens if w.lower() not in stopwords]

def remove_stop_words_without_normalize(tokens):
    """
    Same as remove_stop_words, but tokens passed in are not normalized
    """
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.extend(PATENT_STOPWORDS)
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
    tokens = separate_hypens(tokens)
    tokens = stemmer(tokens)
    return case_folder(tokens)

def separate_hypens(tokens):
    t = []
    for token in tokens:
        t.extend(token.split('-'))
    return t

def get_similar_words(word):
    lemmas_noun = hypernyms_noun = lemmas_verb = hypernyms_verb =[]
    try:
        lemmas_noun =  [str(lemma.name()) for lemma in wn.synset(word + '.n.01').lemmas()]    
    except WordNetError:
        pass

    try:
        hypernyms_noun = [str(lemma.name()).split('.')[0] for lemma in wn.synset(word + '.n.01').hypernyms()]    
    except WordNetError:
        pass

    if len(lemmas_noun) == 0 and len(hypernyms_noun) == 0:
        """
        Only try verbs if there are no similar nouns
        """
        try:
            lemmas_verb =  [str(lemma.name()) for lemma in wn.synset(word + '.v.01').lemmas()]    
        except WordNetError:
            pass

        try:
            hypernyms_verb = [str(lemma.name()).split('.')[0] for lemma in wn.synset(word + '.v.01').hypernyms()]    
        except WordNetError:
            pass
    
    similar_words = lemmas_noun + hypernyms_noun + lemmas_verb + hypernyms_verb
    # filter words which are not purely alphabets (there will be words with underscore)
    # this is because if we want to process such words like "domestic_animal", we have to 
    # implement 2-grams search which is not done here
    pattern = re.compile('^[a-zA-Z]+$')
    return filter(lambda x: pattern.match(x) and x != word, similar_words)
#!/usr/bin/python
import sys
import getopt
import os
import math
from inverted_index import InvertedIndex 
from nltk.tokenize import word_tokenize
import helper

try:
   import cPickle as pickle
except:
   import pickle
import pprint
import xml.etree.ElementTree as ET

pp = pprint.PrettyPrinter(indent=4)

META_DATA = 'meta_data.txt'

def search(dictionary_file, postings_file, query_file, output_file):
    try:
        # Remove previous output file
        os.remove(output_file)
    except OSError:
        pass
    inverted_index = InvertedIndex(dictionary_file, postings_file)
    meta_data = get_meta_data()
    tree = ET.parse(query_file)
    root = tree.getroot()
    tokens = []
    for child in root:
        if child.tag == 'title':
            t = build_tokens(child.text)
            tokens.extend(t)
        elif child.tag == 'description':
            t = build_tokens(child.text)
            tokens.extend(t)

    tokens = helper.remove_stop_words(helper.filter_invalid_characters(tokens))
    results = execute_query(tokens, inverted_index, meta_data)
    write_to_output(output_file, results)


def build_tokens(text):
    tokens = word_tokenize(text)
    return helper.normalize_tokens(tokens)


def get_meta_data():
    f = open(META_DATA, 'r')        
    meta = pickle.loads(f.read())
    f.close()
    return meta

def execute_query(tokens, inverted_index, meta_data):
    query_ltc = get_ltc(tokens, inverted_index.get_dictionary(), meta_data['num_docs'])
    if not query_ltc:
        return []

    doc_lengths = meta_data['doc_lengths']
    scores = Scores()
    for term in tokens:
        postings_list = inverted_index.get_postings_list(term)
        if postings_list:
            for pair in postings_list:
                doc_id = pair[0]
                lnc = get_lnc(pair[1], doc_lengths[doc_id])
                product = lnc*query_ltc[term]
                scores.add_product(doc_id, product)

    return scores.get_top_results()

class Scores:
    def __init__(self):
        self.scores = {}

    def add_product(self, doc_id, product):
        if doc_id not in self.scores:
            self.scores[doc_id] = 0
        self.scores[doc_id] += product

    def get_score(self, doc_id):
        if doc_id not in self.scores:
            return 0
        return self.scores[doc_id]

    def sort_results(self, results):
        return sorted(results, key = lambda result: result['score'], reverse=True)

    def get_doc_id(self, result):
        return result['doc_id']

    def get_top_results(self):
        """
        Returns the top k doc ids ordered by relevance
        For those docs with the same relevance, we further sort them by
        increasing docIds
        """
        results = []
        for key in self.scores:
            results.append({'doc_id': key, 'score': self.scores[key]})
        results = self.sort_results(results)
        return map(self.get_doc_id, results) # no need to return scores


def get_lnc(term_freq, doc_length):
    tf_wt = 1 + math.log(term_freq, 10)
    return tf_wt/doc_length


def get_ltc(tokens, dictionary, num_docs):
    weight = {}
    for token in tokens:
        if token not in weight:
            tf_wt = 1 + math.log(tokens.count(token), 10)
            df = dictionary.get_frequency(token)
            if not df:
                weight[token] = 0
            else:
                idf = math.log(float(num_docs) / df, 10) 
                weight[token] = tf_wt * idf

    sum_of_squares = 0
    for key in weight:
        sum_of_squares += math.pow((weight[key]), 2)
    doc_length = math.sqrt(sum_of_squares)

    if doc_length == 0:
        # All query terms are not found in dictionary
        return None

    for key in weight:
        # normalize weights
        weight[key] = round(weight[key]/doc_length, 2)
    return weight

def file_is_empty(path):
    return os.stat(path).st_size==0

def write_to_output(output_file, results):
    with open(output_file, "a") as f:
        if len(results) == 0:
            f.write('\n')
        else:
            line = ''            
            if not file_is_empty(output_file):
                line = '\n'
            last = len(results) - 1
            for index, result in enumerate(results):
                if index != last:
                    line = line + str(result) + ' '
                else:
                    line += str(result)
            f.write(line)    


def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

if __name__ == '__main__':
    dictionary_file = postings_file = query_file = output_file = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-d':
            dictionary_file = a
        elif o == '-p':
            postings_file = a
        elif o == '-q':
            query_file = a
        elif o == '-o':
            output_file = a
        else:
            assert False, "unhandled option"

    if dictionary_file == None or postings_file == None or query_file == None or output_file == None:
        usage()
        sys.exit(2)

    search(dictionary_file, postings_file, query_file, output_file)
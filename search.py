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

HIGH_PRIORITY_FREQ_THRESHOLD = 4
META_DATA = 'meta_data.txt'
TOP_X_PERCENT_RESULTS = 0.95
top_UPC_classes = []
top_IPC_classes = []
top_family_members = []
top_cited_by = []
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
    title_tokens = []
    description_tokens = []

    raw_tokens = []

    for child in root:
        if child.tag == 'title':
            title_tokens = build_tokens(child.text)
            raw_tokens.extend(word_tokenize(child.text))
        elif child.tag == 'description':
            description_tokens = build_tokens(child.text)
            raw_tokens.extend(word_tokenize(child.text))

    raw_tokens = helper.remove_stop_words_without_normalize(helper.filter_invalid_characters(raw_tokens))
    additional_tokens = []
    for token in list(set(raw_tokens)):
        additional_tokens.extend(helper.get_similar_words(token))
        

    title_tokens = helper.remove_stop_words(helper.filter_invalid_characters(title_tokens))
    description_tokens = helper.remove_stop_words(helper.filter_invalid_characters(description_tokens))

    # tight results are results which favour high precision. We use this as a proxy for true positive
    tight_results = execute_query(title_tokens, description_tokens, [], inverted_index, meta_data)
    global top_UPC_classes
    global top_IPC_classes
    global top_family_members
    global top_cited_by

    # Get top UPC, IPC, family members and cited by from our true positive proxy results
    # This helps us determine which documents are more similar to the original top results
    # when we add in the additional similar words
    top_UPC_classes = get_top_classes(tight_results, meta_data['UPC_class'], 6)
    top_IPC_classes = get_top_classes(tight_results, meta_data['IPC_class'], 4)
    top_family_members = get_top_members(tight_results, meta_data['family_members'], 20)
    top_cited_by = get_top_members(tight_results, meta_data['cited_by'], 20)
    
    # query expansion 
    # supplementary_results = expand_query(tight_results, meta_data['doc_top_terms'], inverted_index, meta_data)
    
    # synonyms, hypernyms
    additional_tokens = helper.normalize_tokens(list(set(additional_tokens)))

    results = execute_query(title_tokens, description_tokens, additional_tokens, inverted_index, meta_data)

    k = int(TOP_X_PERCENT_RESULTS * len(results))
    # j = int(TOP_X_PERCENT_RESULTS * len(supplementary_results))
    # results = list(set(results[:k] + supplementary_results[:j]))
    write_to_output(output_file, results[:k])

def get_top_classes(results, classes, x):
    k = int(0.05 * len(results))
    top_few = results[:k]
    PC = []
    for result in top_few:
        try:
            PC.append(classes[result])
        except KeyError:
            pass
    return helper.get_top_k(PC, x)

def get_top_members(results, classes, x):
    k = int(0.05 * len(results))
    top_few = results[:k]
    members = []
    for result in top_few:
        try:
            members.extend(classes[result])
        except KeyError:
            pass
    return helper.get_top_k(members, x)

def expand_query(results, doc_top_terms, inverted_index, meta_data):
    """
    To deal with the anomalous state of knowledge problem
    We take top 5% of documents. For each document, pick the 10 most frequent non-stop words (already indexed)
    From this pool of words, pick the final top few by frequency.
    Run query again and return results
    """
    k = int(0.05 * len(results))
    top_few = results[:k]
    pool_of_words = []
    for result in top_few:
        pool_of_words.extend(doc_top_terms[result])

    new_query = helper.get_top_k(pool_of_words, 4)
    return execute_query([], new_query, [], inverted_index, meta_data)


def build_tokens(text):
    tokens = word_tokenize(text)
    return helper.normalize_tokens(tokens)


def get_meta_data():
    f = open(META_DATA, 'r')        
    meta = pickle.loads(f.read())
    f.close()
    return meta

def execute_query(title_tokens, description_tokens, additional_tokens, inverted_index, meta_data):
    tokens = title_tokens + description_tokens + additional_tokens
    query_ltc = get_ltc(tokens, inverted_index.get_dictionary(), meta_data['num_docs'])
    if not query_ltc:
        return []

    doc_lengths = meta_data['doc_lengths']
    scores = Scores()
    for term in (tokens):
        high_priority_term = is_high_priority_term(term, title_tokens)

        postings_list = inverted_index.get_postings_list(term)
        if postings_list:
            for pair in postings_list:
                doc_id = pair[0]
                lnc = get_lnc(pair[1], doc_lengths[doc_id])
                
                # Give a boost to this document if its UPC or IPC is inside
                # our top list from the high precision set of results
                boost = 1
                if has_top_UPC_class(doc_id, meta_data):
                    boost += 0.4
                if has_top_IPC_class(doc_id, meta_data):
                    boost += 0.4
                if has_top_family(doc_id, meta_data):
                    boost += 0.4
                if has_top_cited_by(doc_id, meta_data):
                    boost += 0.4

                product = lnc * query_ltc[term] * boost
                scores.add_product(doc_id, product)
                if high_priority_term:
                    scores.increment_high_priority_freq(doc_id)



    return scores.get_top_results()

def has_top_cited_by(doc_id, meta_data):
    try:
        members = meta_data['cited_by'][doc_id]
        for i in range(0, len(members)):
            if members[i] in top_family_members:
                return True
        return False
    except KeyError:
        return False

def has_top_UPC_class(doc_id, meta_data):
    try:
        upc = meta_data['UPC_class'][doc_id]
        return upc in top_UPC_classes
    except KeyError:
        return False

def has_top_IPC_class(doc_id, meta_data):
    try:
        ipc = meta_data['IPC_class'][doc_id]
        return ipc in top_IPC_classes
    except KeyError:
        return False


def has_top_family(doc_id, meta_data):
    try:
        members = meta_data['family_members'][doc_id]
        for i in range(0, len(members)):
            if members[i] in top_family_members:
                return True
        return False
    except KeyError:
        return False


def is_high_priority_term(term, title_tokens):
    """
    A high priority term is one that appears in the query title. This is based on
    the heuristic that a term in the title is usually more important than an 
    arbitrary term in the description.
    """
    return term in title_tokens

class Scores:
    def __init__(self):
        self.scores = {}
        self.high_priority_freq = {}

    def add_product(self, doc_id, product):
        if doc_id not in self.scores:
            self.scores[doc_id] = 0
        if doc_id not in self.high_priority_freq:
            self.high_priority_freq[doc_id] = 0            
        self.scores[doc_id] += product

    def increment_high_priority_freq(self, doc_id):
        self.high_priority_freq[doc_id] += 1

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
        Returns the doc ids ordered by relevance
        """
        results = []
        for key in self.scores:
            score = self.scores[key]
            if self.high_priority_freq[key] >= HIGH_PRIORITY_FREQ_THRESHOLD:
                """
                High priority frequency threshold is crucial in filtering out
                false positives
                """
                score = score * (1 + math.log(self.high_priority_freq[key], 10))

            results.append({'doc_id': key, 'score': score})

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


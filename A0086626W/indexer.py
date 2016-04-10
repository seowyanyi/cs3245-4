#!/usr/bin/python
import re
import nltk
import sys
import math
import os
import indexer
from os import listdir
from os.path import isfile, join
from nltk.tokenize import word_tokenize
from inverted_index import InvertedIndex 
import xml.etree.ElementTree as ET
import helper
        
try:
   import cPickle as pickle
except:
   import pickle

META_DATA = 'meta_data.txt'

def build(index_directory, dictionary_file, postings_file):
    files_to_index = [f for f in listdir(index_directory) if isfile(join(index_directory, f))]
    index = []
    doc_lengths = {}
    counter = 0
    for file_name in files_to_index:
        file_path = format_directory_path(index_directory) + file_name
        # Read XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        tokens = []
        for child in root:
            if child.attrib['name'] == 'Title':
                t = build_tokens(child.text)
                tokens.extend(t)
            elif child.attrib['name'] == 'Abstract':
                t = build_tokens(child.text)
                tokens.extend(t)
        
        tokens = helper.remove_stop_words(helper.filter_invalid_characters(tokens))
        # build tokens
        doc_lengths[remove_file_ext(file_name)] = get_doc_length(tokens)
        index_entries = add_doc_id_to_tokens(tokens, remove_file_ext(file_name))
        index.extend(index_entries)
    #     counter += 1
    #     if counter % 500 == 0:
    #         print 'indexing ............... {}% completed'.format(round(float(counter)/len(files_to_index)*100, 2))
    # print 'Writing index to disk...'
    index = sort_index(index)    
    index = group_index(index)
    write_index_to_disk(index, dictionary_file, postings_file)
    write_meta_data_to_disk(doc_lengths, len(files_to_index))

def remove_file_ext(file_name):
    return os.path.splitext(file_name)[0]

def get_doc_length(tokens):
    tf = {}
    for token in tokens:
        if token not in tf:
            tf[token] = 1 + math.log(tokens.count(token), 10)

    sum_of_squares = 0
    for key in tf:
        sum_of_squares += math.pow((tf[key]), 2)
    return round(math.sqrt(sum_of_squares), 2)

def build_tokens(text):
    tokens = word_tokenize(text)
    return helper.normalize_tokens(tokens)

def format_directory_path(directory_path):
    if directory_path[len(directory_path)-1] != '/':
        return directory_path + '/'
    return directory_path

def write_meta_data_to_disk(doc_lengths, num_docs):
    f = open(META_DATA,'w')
    f.write(pickle.dumps({'doc_lengths': doc_lengths, 'num_docs': num_docs}))
    f.close()


def write_index_to_disk(index, dictionary_file, postings_file):
    """
    Loops through the index and writes to the given dictionary_file and
    postings_file. We have to use the low level os.open and os.write in order to 
    get the exact number of bytes written
    """
    try:
        # Remove previous versions file since this method creates
        # a new one
        os.remove(postings_file)
    except OSError:
        pass

    dictionary = {}
    pointer = 0
    for entry in index:
        postings_list = entry.get_postings_list()
        data_string = pickle.dumps(postings_list)

        fd = os.open(postings_file, os.O_APPEND | os.O_CREAT | os.O_WRONLY)

        num_bytes = os.write(fd, data_string)
        os.close(fd)
        dictionary[entry.get_term()] = {}
        dictionary[entry.get_term()]['pointer'] = pointer
        dictionary[entry.get_term()]['bytes'] = num_bytes        
        dictionary[entry.get_term()]['frequency'] = entry.get_frequency()

        pointer += num_bytes

    f = open(dictionary_file,'w')
    f.write(pickle.dumps(dictionary))
    f.close()
    

def inverted_index_to_string(ii):
    """
    For debugging purposes
    """
    s = '{:<10}   {:>5}\t     {:>20}\n'.format('term', 'frequency', 'postings list')    
    for elem in ii:
        s += '{:<10}   {:>5}\t --> {:<10}\n'.format(elem.get_term(), elem.get_frequency(), elem.get_postings_list())
    return s

def sort_index(index):
    return sorted(index, key = lambda entry: (entry['term'], entry['doc_id']))

def group_index(index):
    """
    Groups identical terms in the index, recording their frequency and postings list
    """
    grouped_index = []
    last = len(index) - 1
    previous = {'term': None, 'doc_id': None}
    entry = None
    termFreq = 0

    for i, element in enumerate(index):
        if element['term'] == previous['term']:
            if element['doc_id'] == previous['doc_id']:
                termFreq += 1
            else:
                entry.add_document(previous['doc_id'], termFreq)  
                termFreq = 1 # set term frequency counter to 1 for the new document              
        else:
            if entry is not None: 
                entry.add_document(previous['doc_id'], termFreq)                  
                grouped_index.append(entry)
            entry = IndexEntry(element['term'])
            termFreq = 1                

        previous = element
        
        if i == last:
            grouped_index.append(entry)
            
    return grouped_index

class IndexEntry:
    def __init__(self, term):
        self.term = term
        self.docFreq = 0
        self.postings_list = []  
        self.sorted = True

    def add_document(self, doc_id, termFreq):
        self.docFreq += 1
        self.postings_list.append((doc_id, termFreq))
        self.sorted = False        

    def get_postings_list(self):
        if not self.sorted:
            self.postings_list = sorted(self.postings_list, key=lambda tup: tup[0])
            self.sorted = True
        return self.postings_list

    def get_frequency(self):
        return self.docFreq

    def get_term(self):
        return self.term


def add_doc_id_to_tokens(tokens, doc_id):
    return [{'term': token, 'doc_id': doc_id} for token in tokens]


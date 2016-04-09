#!/usr/bin/python
import re
import sys
import getopt
import os
import indexer
from os import listdir
from os.path import isfile, join

try:
   import cPickle as pickle
except:
   import pickle
import pprint
pp = pprint.PrettyPrinter(indent=4)

def build_index(index_directory, dictionary_file, postings_file):
    indexer.build(index_directory, dictionary_file, postings_file)


def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

index_directory = dictionary_file = postings_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        index_directory = a
    elif o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    else:
        assert False, "unhandled option"
if index_directory == None or dictionary_file == None or postings_file == None:
    usage()
    sys.exit(2)

build_index(index_directory, dictionary_file, postings_file)
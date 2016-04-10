#!/usr/bin/python
import sys
import getopt
import os
import math
import xml.etree.ElementTree as ET
from collections import Counter

def evaluate(result_file, positive, negative):
    results = []
    positive_docs = []
    negative_docs = []

    with open(result_file) as r:
        read_data = r.read()
        results = read_data.split()
    with open(positive) as p:
        positive_docs = p.read().splitlines()
    with open(negative) as n:
        negative_docs = n.read().splitlines()
    
    tp = fp = fn = 0

    for i in range(0, len(results)):
        result = results[i]
        if result in positive_docs:
            tp += 1
            print 'True positive {} \t{}/{}'.format(result, i+1, len(results))

    for i in range(0, len(results)):
        result = results[i]
        if result in negative_docs:
            fp += 1
            print 'False positive {} \t{}/{}'.format(result, i+1, len(results))

    for doc in positive_docs:
        if doc not in results:
            fn += 1
            print 'False negative {}'.format(doc)
            

    if tp == 0 and fp == 0:
        P = 0
    else:      
        P = float(tp)/(tp + fp)
    
    if tp == 0 and fn == 0:
        R = 0
    else:
        R = float(tp)/(tp + fn)            

    print 'Num results: {}'.format(len(results))
    print 'Precision: {}'.format(P)
    print 'Recall: {}'.format(R)

    if p == 0 and R == 0:
        print 'F2 is 0'
    else:        
        print 'F2: {}'.format(2*P*R/(2*P + R))


def get_top_k(items, k):
    """
    Returns the top k most frequent occurences in items
    """
    counts = Counter(items)
    return counts.most_common(k)


def usage():
    print "Oops"

if __name__ == '__main__':
    result_file = positive = negative = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'r:p:n:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-r':
            result_file = a
        elif o == '-p':
            positive = a
        elif o == '-n':
            negative = a
        else:
            assert False, "unhandled option"

    if result_file == None or positive == None or negative == None:
        usage()
        sys.exit(2)

    evaluate(result_file, positive, negative)


        # testing
    # top_UPC_classes = []
    # top_IPC_groups = []
    # for i in range(0, 100):
    #     result = results[i]
    #     tree = ET.parse('patsnap-corpus/' + result + '.xml')
    #     root = tree.getroot()

    #     for child in root:
    #         if child.attrib['name'] == 'UPC Class':
    #             top_UPC_classes.append(child.text.strip())
    #         elif child.attrib['name'] == 'IPC Group':
    #             top_IPC_groups.append(child.text.strip())

    # print get_top_k(top_UPC_classes, 15)
    # print get_top_k(top_IPC_groups, 15)



    # return

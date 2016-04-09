#!/usr/bin/python
import sys
import getopt
import os
import math

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

    for result in results:
        if result in positive_docs:
            tp += 1

    for doc in positive_docs:
        if doc not in results:
            fn += 1

    for result in results:
        if result in negative_docs:
            fp += 1
    
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
        print 'F2: {}'.format(5*P*R/(4*P + R))

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
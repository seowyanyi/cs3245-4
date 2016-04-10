#!/usr/bin/python
import sys
import getopt
import os
import math
import xml.etree.ElementTree as ET

def examine(pos, neg):
    positive_results = []
    negative_results = []
    with open(pos) as p:
        positive_results = p.read().splitlines()
    with open(neg) as n:
        negative_results = n.read().splitlines()

    print '\n\nTrue positive: ------------------------------- '
    UPC_classes = []
    IPC_groups = []
    for f in positive_results:
        tree = ET.parse('patsnap-corpus/' + f + '.xml')
        root = tree.getroot()

        for child in root:
            if child.attrib['name'] == 'UPC Class':
                UPC_classes.append(child.text.strip())
            elif child.attrib['name'] == 'IPC Subclass':
                IPC_groups.append(child.text.strip())
    UPC_classes =  list(set(UPC_classes))    
    # for i in UPC_classes:
    #     print i            
    IPC_groups =  sorted(list(set(IPC_groups)))
    for i in IPC_groups:
        print i            

    print '\n\nTrue negative: -------------------------------'
    UPC_classes = []
    IPC_groups = []

    for f in negative_results:
        tree = ET.parse('patsnap-corpus/' + f + '.xml')
        root = tree.getroot()

        for child in root:
            if child.attrib['name'] == 'UPC Class':
                UPC_classes.append(child.text.strip())
            elif child.attrib['name'] == 'IPC Subclass':
                IPC_groups.append(child.text.strip())
    UPC_classes =  list(set(UPC_classes))    
    # for i in UPC_classes:
    #     print i            
    IPC_groups =  sorted(list(set(IPC_groups)))
    for i in IPC_groups:
        print i            

    # true_positive = []
    # for f in positive_results:
    #     tree = ET.parse('patsnap-corpus/' + f + '.xml')
    #     root = tree.getroot()

    #     for child in root:
    #         if child.attrib['name'] == 'Family Members':
    #             members = child.text.strip().split('|')
    #             true_positive.extend(members)
    # print 'True positive: ------------------------------- '
    # for f in positive_results:
    #     print calculate_similarity(f, true_positive)

    # print 'True negative: -------------------------------'
    # for f in negative_results:
    #     print calculate_similarity(f, true_positive)

def calculate_similarity(f, true_positive):
    set_of_true_pos = list(set(true_positive))
    tree = ET.parse('patsnap-corpus/' + f + '.xml')
    root = tree.getroot()
    matches = 0
    members = []
    for child in root:
        if child.attrib['name'] == 'Family Members':
            members = child.text.strip().split('|')
            for m in members:
                if m in true_positive:
                    matches += 1
    if len(set_of_true_pos) == 0:
        return 0                    
    return float(matches)/len(set_of_true_pos)*100

def usage():
    print "Oops"

if __name__ == '__main__':
    pos = neg = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:n:')
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-p':
            pos = a
        elif o == '-n':
            neg = a            
        else:
            assert False, "unhandled option"

    if pos == None or neg == None:
        usage()
        sys.exit(2)

    examine(pos, neg)
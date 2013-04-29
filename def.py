#!/usr/bin/env python

import textwrap, sys
from nltk.corpus import wordnet as wn

class bcolors:
    HEADER = '\033[97m'
    OKBLUE = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

POS = {
    'v': 'verb', 'a': 'adjective', 's': 'satellite adjective', 
    'n': 'noun', 'r': 'adverb'}

def info(word, pos=None):
    for i, syn in enumerate(wn.synsets(word, pos)):
        syns = [n.replace('_', ' ') for n in syn.lemma_names]
        ants = [a for m in syn.lemmas for a in m.antonyms()]
        ind = ' '*12
        defn= textwrap.wrap(syn.definition, 64)
        print bcolors.OKGREEN + 'sense %d (%s)' % (i + 1, POS[syn.pos]) + bcolors.ENDC
        print bcolors.WARNING + 'definition: ' + ('\n' + ind).join(defn) + bcolors.ENDC
        print bcolors.OKBLUE + '  synonyms:', ', '.join(syns)
        if ants:
            print '  antonyms:', ', '.join(a.name for a in ants)
        if syn.examples:
            print '  examples: ' + ('\n' + ind).join(syn.examples)
        print bcolors.ENDC

if len(sys.argv)==2:
    info(sys.argv[1])
else:
    print "Usage: def.py <word>"
    sys.exit()

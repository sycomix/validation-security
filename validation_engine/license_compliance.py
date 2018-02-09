#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ================================================================================
# ACUMOS
# ================================================================================
# Copyright © 2017 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
# ================================================================================
# This Acumos software file is distributed by AT&T and Tech Mahindra
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ================================================================================


"""
The following program is a Ninka is a lightweight license identification tool for source code. It is sentence-based, and provides a simple way to identify open source licenses in a source code file. It is capable of identifying several dozen different licenses (and their variations).
"""


import re
from collections import Counter


def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('big.txt').read()))

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

More_permission = ["PSFL","MIT","MIT (X11)", "New BSD", "ISC", "Apache" ]

Less_permissive = ["LGPL","GPL", "GPLv2", "GPLv3"]

Dict1 = {
"boostV1Ref" : "boostV1",
    "X11" : "X11mit",
    "X11Festival" : "X11mit",
    "X11mitNoSellNoDocDocBSDvar" : "X11mit",

    "X11mitwithoutSell" : 'X11mit',
    "X11mitBSDvar" : "X11mit",
    "X11mitwithoutSellCMUVariant" : "X11mit",
    "X11mitwithoutSellCMUVariant": "X11mit",
    "X11mitwithoutSellandNoDocumentationRequi" : "X11mit",
    "MITvar3" : "X11mit",
    "MITvar2" : "X11mit",
    "MIT" : "X11mit",
    "ZLIBref" : "ZLIB",
    "BSD3NoWarranty" : "BSD3",
    "BSD2EndorseInsteadOfBinary" : "BSD2",
    "BSD2var2" : "BSD2",
    "LesserGPLv2" : "LibraryGPLv2",
    "LesserGPLv2+"  : "LibraryGPLv2+",
    "orLGPLVer2.1" : "LesserGPLVer2.1",
    "postgresqlRef" : "postgresql"
    }

text = " MIT license is embedded in thisprogram"

list1 = text.split()

def License_compliance1():
    for i in list1:
        if i in Less_permissive:
            return ( 'Fail')
        else:
            return ("Pass")

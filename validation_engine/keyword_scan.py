#! python
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

import gensim

def readfile(filename, keyword):

# read file
    with open(filename) as file_search:   #open search file
        file_search = file_search.readlines()   #read file
    saved_word = [lines for lines in file_search if keyword in lines]
    with open('CompleteResponse.txt', 'w') as file_handler:
        file_handler.write(f"{filename}\n")
        for item in saved_word:
            file_handler.write(f"{item}")

    print('done') # completed

    print(len(saved_word)) # count found words





striptext = text.replace('\n\n', ' ')
striptext = striptext.replace('\n', ' ')


keywords = gensim.summarization.keywords(striptext)
print(keywords)
keywords_list = keywords.split()


dict = []

def keyword_scan():
    for i in keywords_list:
        return "Fail" if i in dict else "Pass"

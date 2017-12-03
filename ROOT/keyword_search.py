import gensim
import os
import sys


def readfile(filename, keyword):

    saved_word = []
# read file
    with open(filename) as file_search:   #open search file
        file_search = file_search.readlines()   #read file
    for lines in file_search:    # every word is scaned
           if keyword in lines:   # extract the keyword
                saved_word.append(lines)    #store all found keywords in array
        # write in new file
    with open('CompleteResponse.txt', 'w') as file_handler:
        file_handler.write(f"{filename}\n")
        for i in range(len(saved_word)):
            file_handler.write(f"{saved_word[i]}")

    print('done') # completed

    print(len(saved_word)) # count found words





striptext = text.replace('\n\n', ' ')
striptext = striptext.replace('\n', ' ')


keywords = gensim.summarization.keywords(striptext)
print(keywords)
keywords_list = keywords.split()


dict = ['verizon', 'AT&T']

def keyword_search():
    for i in keywords_list:
        if i in dict:
            return "Fail"
    
        else:
            return "Pass"

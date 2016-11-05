import numpy as np
import os, sys, StringIO, re
import xml.etree.ElementTree as ET
from nltk import ngrams,word_tokenize,pos_tag,sent_tokenize
from nltk.parse import stanford
from collections import Counter
import pickle

dir_path = os.path.dirname(os.path.realpath(__file__))
metric_list = ['BLEU', 'Rouge', 'DICE', 'Jaccard']

def getPatterns(text,metrics):
    before=set()
    after=set()
    patterns = []
    try :
        # print text
        # print '\nYoho'+ metrics
        sentences = sent_tokenize(text)
        # print ('\nYOsh\n')
        # print sentences
        for sent in sentences :
            # print len(sentences)
            words = word_tokenize(sent)
            n = len(words)
            for i in xrange(n):
                s = ""
                if words[i] == metrics :
                    # print words
                    if i>=2:
                        # before.add((words[i-2],word[i-1]))
                        s += (words[i-2] + ' ') 
                    if i>=1:
                        # before.add(words[i-1])
                        s += (words[i-1] + ' ')
                        s += (metrics + ' ')
                    if i<n-1:
                        # after.add(words[i+1])
                        if i < 1 :
                            s += (metrics + ' ')
                        s += (words[i+1] + ' ')
                            
                    if i<n-2:
                        # after.add((words[i+1],words[i+2]))
                        s += (words[i+2] + ' ')
                    patterns.append(s)
    except:
        pass
    # return before,after,patterns
    return patterns

def isNoun(words,text):
    tags = pos_tag(words)
    print tags
    for tag in tags :
        if tag[1] != 'NN' and tag[1] != 'NNP' and tag[1] != 'NNS':
            return False
    return True

def getMaxWordLength(patterns):
    max_length=0
    for pattern in patterns:
        max_length=max(max_length,len(pattern.split(' ')))
    return max_length

def pattern_annotate(metrics):
    all_patterns = []
    try:
        tree=ET.parse(file_path)
        root=tree.getroot()
        for section in root.findall('section'):
            for chunk in section.findall('chunk'):
                # print chunk.text
                patterns=getPatterns(chunk.text.lower(),metrics.lower())
                all_patterns += patterns
    except:
        pass #e.printStackTrace()
    count = Counter(all_patterns)
    print len(all_patterns)
    patterns = count.items()
    print patterns
    print '\nPart 1 end\n'
    # all_after = set()
    # all_before = set()
    # pattern_tuples = set()
    # for i in xrange(0, len(patterns)):
    #     k = patterns[i][0]
    #     # print k + '\n'
    #     k = k.split(' ')
    #     for ek in xrange(len(k)):
    #         if k[ek] == metrics.lower() :
    #             try:
    #                 # print k[ek-1]
    #                 # print '\n'
    #                 # print k[ek+1]
    #                 pattern_tuples.add((k[ek-2],k[ek-1],k[ek],k[ek+1],k[ek+2]))   
    #                 all_before.add((k[ek-2],k[ek-1]))
    #                 all_after.add((k[ek+1],k[ek+2]))
    #                 # for bef in k[:ek] :
    #                 #     all_before.add(bef)
    #                 # for aft in k[ek+1:] :
    #                 #     all_after.add(aft)
    #             except:
    #                 continue
    # print pattern_tuples
    # print '\n\n'
    # print all_before
    # print '\n\n'
    # print all_after
    # print '\nPart 2 end\n'
    return count
metric_patterns = list()
for metric in metric_list:
    metric_pattern_counter = Counter()        
    print '\n' + metric + '\n'
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            if (os.path.join(subdir, file)).endswith('.xml'):
                file_path = os.path.join(subdir, file)
                print '\n\nNew File: ' + file_path +'\n\n'
                perfile_counter = pattern_annotate(metric)
                perfile_patterns = perfile_counter.most_common()
                metric_pattern_counter = metric_pattern_counter + perfile_counter

                delete_indices = []
                for i in xrange(0, len(perfile_patterns)):
                    if len(re.findall ('[^\w\d\s]+', perfile_patterns[i][0])) == 0 and perfile_patterns[i][0].find('_') == -1:
                        continue
                    else:
                        delete_indices.append(i)
                # print delete_indices
                for i in xrange(len(delete_indices)-1, -1, -1):
                    perfile_patterns.pop(delete_indices[i])

                temp_file_name = file_path[:-4]
                temp_file_name = temp_file_name + '_' + metric + '.txt'
                # f1 = open(temp_file_name,'w')
                # for i in xrange(0, len(perfile_patterns)):
                #     print >>f1, perfile_patterns[i]
                #     print '\n'
                # f1.close()
                temp_file_name = temp_file_name[:-4]
                temp_file_name = temp_file_name + '.pkl'
                # f1 = open(temp_file_name,'wb')
                # pickle.dump(perfile_patterns, f1, -1)
                # f1.close()

    metric_file = dir_path + '/' + metric + '_train.txt'
    # f2 = open(metric_file,'w')
    metric_patterns += metric_pattern_counter.most_common()

    delete_indices_new = []
    for i in xrange(0, len(metric_patterns)):
        if len(re.findall ('[^\w\d\s]+', metric_patterns[i][0])) == 0 and metric_patterns[i][0].find('_') == -1:
            continue
        else:
            delete_indices_new.append(i)
    for i in xrange(len(delete_indices_new)-1, -1, -1):
        metric_patterns.pop(delete_indices_new[i])
    
    # for i in xrange(0, len(metric_patterns)):
    #         print >>f2, metric_patterns[i] 
    #         print '\n'
    # f2.close()
    
    metric_file = metric_file[:-4]
    metric_file = metric_file + '.pkl'
f2 = open("output_patterns.txt", 'wb')
pickle.dump(metric_patterns, f2, -1)
f2.close()

print "\nWe're done"

    
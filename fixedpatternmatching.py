import os
import xml.etree.ElementTree as ET
from nltk import ngrams,word_tokenize,pos_tag,sent_tokenize
from nltk.parse import stanford
from nltk.stem import WordNetLemmatizer
from collections import Counter
import pickle
import re

def isNoun(words,text):
	i = 0
	words = words.split(' ')
	tags = pos_tag(text)
	for tag in tags :
		if tag[0] == words[i] :
			i += 1
			if tag[1] != 'NN' and tag[1] != 'NNP':
				return False
			if i >= len(words): break
	return True

def Hmean(i,j):
	if i == 0 or j == 0 :
		return 0
	return (2*i*j)/(i+j)

def evaluateFromPattern(metricCount,gold_metrics):
	# patterns_count = counter of all_patterns, gold_patterns_count = list with elements as (pattern, count)
	gold_list = ['bleu','rouge','dice','jaccard','meteor']
	if isinstance(metricCount,dict) == False :
		dict1 = {}
		for i in metricCount :
			dict1[i[0]] = i[1]
		metricCount = dict1
	gold_metric_dict=Counter()
	for m in gold_list:
		gold_metric_dict[m]=0
		for k in gold_metrics:
			if m in k[0]:
				gold_metric_dict[m]+=k[1]
	if isinstance(metricCount,dict) == False :
		dict1 = {}
		for i in metricCount :
			dict1[i[0]] = i[1]
		metricCount = dict1
	# print gold_metric_dict
	p_num=0
	p_denom=float(sum(metricCount.values()))
	r_num=0
	r_denom= float(sum(gold_metric_dict.values()))
	correct = {}
	false = {}
	for metric in metricCount.keys():
		q = False
		for m in gold_list:
			if q == True :
				break
			if m in metric:
				q = True
				correct[metric] = metricCount[metric]
				p_num+=metricCount[metric]
				r_num+=metricCount[metric]
		if q== False :
			false[metric] = metricCount[metric]
	# print correct 
	# print false
	# print p_num, p_denom, r_num,r_denom
		# # for pattern in gold_metrics:
		# # 	if metric in pattern :
		# # 		p_num += 1
		# words = word_tokenize(metric)
		# if len(words) > 1 :
		# 	for gold in gold_list :
		# 		if gold in metric :
		# 			p_num += 1
		# 			r_num += 1
		# 			break
		# else :
		# 	if words[0] in gold_list :
		# 		p_num += 1
		# 		r_num += 1
	# print p_num,p_denom,r_denom
	# if p_denom == 0 or r_denom == 0 :
		# return 0 , 0,0,0	
	# p=float(p_num)/float(p_denom)
	# r=float(r_num)/float(r_denom)
	return p_num,p_denom,r_num,r_denom

def getXML(pdf_files,pdf_folder,ocr_folder,xml_folder):
	try:
		os.mkdir(xml_folder)
	except:
		pass
	for pdf in pdf_files:
		if pdf[-4:]!='.pdf':
			continue
		xml_name=pdf[:-3]+'xml'
		print xml_name
		os.system('cp '+pdf_folder+pdf+' '+ocr_folder+'input.pdf')
		os.system('python '+ocr_folder+'main_script_batch.py')
		os.system('cp '+ocr_folder+'Secmap.xml '+xml_folder+xml_name)

def getPatterns(text,metrics):
	remove={',','(',')',':','.','"',';','[',']','{','}','|','-','_'}
	wnl = WordNetLemmatizer()
	patterns = []
	try :
		sentences = sent_tokenize(text)
		for sent in sentences :
			words = word_tokenize(sent)
			n = len(words)
			for i in xrange(n):
				s = ""
				if words[i] == metrics :
					if i>=1 and i<n-1:
						if words[i-1] not in remove and words[i+1] not in remove:
							s+=words[i-1]+' '+metrics+' '+words[i+1]
					# if i>=2 and i<n-2:
					# 	s+=words[i-2]+' '+words[i-1]+' '+metrics+' '+words[i+1]+' '+words[i+2]
					if s!="":
						patterns.append(s)
	except :
		pass
	return patterns

def getNGrams(text,n):
	ret = ngrams(word_tokenize(text),n)
	return ret

def train(xml_folder_test,xml,metrics):
	all_patterns = []
	try:
			tree=ET.parse(xml_folder_test+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					for metric in metrics :
						patterns=getPatterns(chunk.text.lower(),metric.lower())
						all_patterns += patterns
	except :
			pass
	counter = Counter(all_patterns)
	print "Done with Training on file %s" % (xml) 
	return all_patterns

def test(xml_folder_eval,xml,all_before,all_after):
	new_metrics= []
	new_patterns = []
	try:
			tree=ET.parse(xml_folder_eval+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					n_grams=getNGrams(chunk.text.lower(),5)
					b1 = False
					for n_gram in n_grams:
						for i in n_gram :
							if i 	in all_before :
					 			b_index = n_gram.index(i)
								for a in all_after:
									try:
										a_index=n_gram.index(a)
									except :
										a_index = -1
									if a_index!=-1 and a_index > b_index + 1:
										possible_metric = ""
										metric_len = 0
										for ind in range(b_index+1,a_index):
											metric_len += 1
											possible_metric += n_gram[ind] +  " "
										possible_metric = possible_metric.rstrip()
										possible_pattern = ""
										for ind in range(b_index,a_index+1):
											possible_pattern += n_gram[ind] +  " "
										possible_pattern = possible_pattern.rstrip()
										if isNoun(possible_metric,list(n_gram)) == True :
											if b_index == 1	:
												b1 = True
												new_metrics.append(possible_metric)
												new_patterns.append(' '.join(n_gram[b_index:a_index+1]))
												break
											if b_index == 0 :
												if b1 == True :
													b1 = False
												else :
													new_metrics.append(possible_metric)
													new_patterns.append(' '.join(n_gram[b_index:a_index+1]))
													break


	except:
		pass
	# print new_metrics
	return new_metrics, new_patterns

def getScore(xml,metricCount,cutoff):
	try:
		gold_metrics = pickle.load(open("./annotFiles/"+xml[:-3] + "pkl"))
	except:
		print "%d\tall\t%f\t%f\t%f" % (cutoff,0,0,0)
		return		
	p_num,p_denom,r_num,r_denom = evaluateFromPattern(metricCount,gold_metrics)
	if p_denom == 0 or r_denom == 0:
		prec = 0
		rec = 0
	else :
		prec=float(p_num)/float(p_denom)
		rec=float(r_num)/float(r_denom)		
	if rec > 1 :
		rec = 1
	print "%d\t%d\t%d\t%d\t%f\t%f\t%f" % (p_num,p_denom,r_num,r_denom,prec, rec,Hmean(prec,rec))
	# print metricCount, xml
	# top = 10
	# while top > 0 :
	# 	# print patternCount.most_common(top)
	# 	prec,rec = evaluateFromPattern(metricCount.most_common(top),gold_metrics)
	# 	if rec > 1 :
	# 		rec = 1
	# 	print "%d\t%d\t%f\t%f\t%f" % (cutoff,top,prec,rec,Hmean(prec,rec))
	# 	# if top <= 10 :
	# 	# 	print metricCount.most_common(top)	
	# 	top -= 10


def indTrain(metrics,cutoff):
	pdf_folder_test='./Trainer/'
	pdf_folder_eval = './Tester/'
	ocr_folder='/Users/poorvadixit/Desktop/studies/NLP/SNLP-2016-master 2/'
	pdf_files_test=os.listdir(pdf_folder_test)
	xml_folder_test=pdf_folder_test+ "xmlfiles/"
	pdf_files_eval=os.listdir(pdf_folder_eval)
	xml_folder_eval=pdf_folder_eval+ "xmlfiles/"
	# getXML(pdf_files_test,pdf_folder_test,ocr_folder,xml_folder_test)
	# getXML(pdf_files_eval,pdf_folder_eval,ocr_folder,xml_folder_eval)
	xml_files_test=os.listdir(xml_folder_test)
	all_before=set(' ')
	all_after=set(' ')
	all_patterns = []
	for xml in xml_files_test:
		all_patterns += train(xml_folder_test,xml,metrics)
	counter = Counter(all_patterns)
	print "Done with Training"
	all_before = set()
	pattern_tuples = set()
	if cutoff == 0 :
		counter = counter.most_common()
	else :
		counter = counter.most_common(cutoff) 
	for i in counter:
		k = i[0]
		k = word_tokenize(k)
		for ek in xrange(len(k)):
			for metric in metrics :
				if k[ek] == metric.lower() :
					try:
						all_before.add(k[ek-1])
					except :
						pass
					try:
						all_after.add(k[ek+1])
					except :
						pass
	n = 5
	new_metrics= []
	new_patterns = []
	xml_files_eval = os.listdir(xml_folder_eval)
	tot = len(xml_files_eval)
	count = 0
	for xml in xml_files_eval:
		count += 1
		print "%d file out of %d files" % (count, tot)
		new_patterns, new_metrics = test(xml_folder_eval,xml,all_before,all_after)
		getScore(xml,Counter(new_metrics),cutoff)

def bootstrap(metrics,cutoff):
	xml_folder_test="/Users/poorvadixit/Desktop/studies/NLP/SNLP-2016-master 2/Trainer/xmlfiles/"
	xml_files_test = os.listdir(xml_folder_test)
	xml_folder_eval="/Users/poorvadixit/Desktop/studies/NLP/SNLP-2016-master 2/Tester/xmlfiles/"
	xml_files_eval = os.listdir(xml_folder_eval)
	all_patterns=[]
	for xml in xml_files_test:
		try:
			tree=ET.parse(xml_folder_test+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					for metric in metrics:
						patterns=getPatterns(chunk.text.lower(),metric.lower())
						all_patterns += patterns
					# re.sub(r'[^\w]', ' ', patterns)
					# print patterns
		except :
			pass
	# print all_patterns
	ordered_patterns = Counter(all_patterns)
	# print ordered_patterns
	new_metrics=[]
	n=5
	for xml in xml_files_eval:
		try:
			tree=ET.parse(xml_folder_eval+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					n_grams=ngrams(chunk.text.lower().split(),3)
					n_grams=list(n_grams)
					for n_gram in n_grams:
						for top in ordered_patterns.most_common(cutoff):
							if n_gram[0]==top[0].split()[0] and n_gram[2]==top[0].split()[2] :
								# print n_gram
								if isNoun(n_gram[1],n_gram)==True:
									new_metrics.append(n_gram[1])
		except Exception as e:
			# print e
			pass
	# pattern_count=Counter(new_metrics)
	# for key,value in pattern_count.most_common():
		# print key,value
	# print pattern_count
	# for i in range(len(pattern_count)):
	# 	print pattern_count[i]
	metricCount = Counter(new_metrics)
	new_metric_count= Counter()
	for metric in metricCount:
		if metricCount[metric]>2	:
			new_metric_count[metric]=metricCount[metric]
	metricCount=new_metric_count
	# patternCount = Counter(new_patterns)

	count = 0
	# for i in metricCount.items():
	# for i in metricCount.most_common(50):
	# for i in patternCount.items():
	# for i in patternCount.most_common(5):
		# count += i[1]
		# print "%s 				%d" %(i[0],i[1])

	# print "Total = %d" % count
	print "Training done."	
	print "Start the evaluation."
	gold_metrics = pickle.load(open("SNLP-2016-master 2/output_patterns.p"))
	p_num,p_denom,r_num,r_denom = evaluateFromPattern(metricCount,gold_metrics)
	if p_denom == 0 or r_denom == 0:
		prec = 0
		rec = 0
	else :
		prec=float(p_num)/float(p_denom)
		rec=float(r_num)/float(r_denom)
	if rec > 1 :
		rec = 1
	print "Cutoff 	Top 	Precison 	Recall 	fScore"
	print "%d\t%d\t%f\t%f\t%f" % (cutoff,len(metricCount.keys()),prec, rec,Hmean(prec,rec))

	# print "%d\t%d\t%f\t%f\t%f" % (cutoff,len(metricCount.keys()),prec, rec,Hmean(prec,rec))
	while cutoff is not 10:
		top = 25
		while top > 0 :
			# print patternCount.most_common(top)
			p_num,p_denom,r_num,r_denom = evaluateFromPattern(metricCount.most_common(top),gold_metrics)
			if p_denom == 0 or r_denom == 0:
				prec = 0
				rec = 0
			else :
				prec=float(p_num)/float(p_denom)
				rec=float(r_num)/float(r_denom)
			if rec > 1 :
				rec = 1
			# print "%d\t%d\t%f\t%f\t%f" % (cutoff,top,prec,rec,Hmean(prec,rec))
			print "%d\t%d\t%f\t%f\t%f" % (cutoff,top,prec, rec,Hmean(prec,rec))		
			# if top <= 10 :
			# 	print metricCount.most_common(top)	
			top -= 5
		cutoff+=5
		
cutoff = 5
bootstrap(["ROUGE","BLEU","DICE","JACCARD"],cutoff)
	# indTrain(["ROUGE","BLEU","DICE","JACCARD"],cutoff)
# bootstrap(["ROUGE","BLEU","DICE","JACCARD"],0)
	























import os
import xml.etree.ElementTree as ET
from nltk import ngrams,word_tokenize,pos_tag,sent_tokenize
from nltk.parse import stanford
from collections import Counter
# from nltk.tag import StanfordPOSTagger 
import pickle
import re

# path_to_jar = "/home/vadde/Documents/Stanford/stanford-corenlp-3.6.0.jar"
# model_filename = "/home/vadde/Documents/Stanford/stanford-corenlp-3.6.0-models/edu/stanford/nlp/models/pos-tagger/english-left3words/english-left3words-distsim.tagger"
# st = StanfordPOSTagger(model_filename =model_filename,path_to_jar = path_to_jar)


def stanTag(words):
	tags = st.tag(words)
	for tag in tags :
		if tag[1] != 'NN' and tag[1] != 'NNP':
			return False
	return True


def Hmean(i,j):
	if i == 0 or j == 0 :
		return 0
	return (2*i*j)/(i+j)

def evaluate(metricCount,gold_metrics):
	# patterns_count = counter of all_patterns, gold_patterns_count = list with elements as (pattern, count)
	if isinstance(metricCount,dict) == False :
		dict1 = {}
		for i in metricCount :
			dict1[i[0]] = i[1]
		metricCount = dict1
	p_num=0
	p_denom=float(len(metricCount.keys()))
	r_num=0
	r_denom= float(len(gold_metrics))
	for metric in metricCount.keys():
		if metric in gold_metrics :
				p_num += 1
	
	# print p_num,p_denom,r_denom
	p=float(p_num)/float(p_denom)
	r=float(p_num)/float(r_denom)
	return p,r

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
			if m in k:
				gold_metric_dict[m]+=gold_metrics[k]
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
	# print gold_metric_dict
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
	before=set()
	after=set()
	patterns = []
	try :
		sentences = sent_tokenize(text)
		for sent in sentences :
			words = word_tokenize(sent)
			n = len(words)
			for i in xrange(n):
				s = ""
				if words[i] == metrics :
					if i>=2:
						s += (words[i-2] + ' ') 
					if i>=1:
						s += (words[i-1] + ' ')
						s += (metrics + ' ')
					if i<n-1:
						if i < 1 :
							s += (metrics + ' ')
						s += (words[i+1] + ' ')		
					if i<n-2:
						s += (words[i+2] + ' ')
					patterns.append(s)
	except :
		pass
	return patterns

def getNGrams(text,n):
	ret = ngrams(word_tokenize(text),n)
	return ret

def isNoun(words,text):
	# if len(words) == 1:
	# 	return False
	if len(re.findall('[^A-Za-z ]',words))>0:return False
	i = 0
	tags = pos_tag(word_tokenize(words))
	words=word_tokenize(words)
	for w in words:
		if len(w)==1:return False
	for tag in tags :
		if tag[0] == words[i] :
			i += 1
			if tag[1] != 'NN' and tag[1] != 'NNP':
				return False
			if i >= len(words): break
	return True

def getMaxWordLength(patterns):
	max_length=0
	for pattern in patterns:
		max_length=max(max_length,len(pattern.split(' ')))
	return max_length

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
	ocr_folder='/var/www/html/OCR++/myproject/media/documents/'
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
	pdf_folder_test='./Trainer/'
	pdf_folder_eval = './Tester/'
	ocr_folder='/var/www/html/OCR++/myproject/media/documents/'
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
	# print counter
	print "Total Patterns =%d, freq = %d"%(len(counter.keys()),sum(counter.values()))
	# return
	print "Done with Training"
	all_after = set()
	all_before = set()
	pattern_tuples = set()
	if cutoff == 0 :
		counter = counter.most_common()
	else :
		print 'Cutoff:',cutoff
		counter = counter.most_common(cutoff) 
	# print count
	# print counter
	# return 
	for i in counter:
	# for i in all_patterns :
		k = i[0]
		k = word_tokenize(k)
		# k = word_tokenize(i)
		for ek in xrange(len(k)):
			for metric in metrics :
				if k[ek] == metric.lower() :
					# pattern_tuples.add((k[ek-1],k[ek+1]))	
					try:
						all_before.add((k[ek-2],k[ek-1]))
					except :
						pass
					try:
						all_after.add((k[ek+1],k[ek+2]))
					except :
						pass
	# print all_before
	# print all_after
	print 'All Before count =',len(all_before)
	print 'All After count =',len(all_after)
	count = 0
	n = 5
	new_metrics= []
	new_patterns = []
	xml_files_eval = os.listdir(xml_folder_eval)
	print "Starting to get patterns"
	tot = len(xml_files_eval)
	for xml in xml_files_eval:
		count += 1
		# print "%d file out of %d files" % (count, tot)
		try:
			tree=ET.parse(xml_folder_eval+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					n_grams=getNGrams(chunk.text.lower(),n)
					for n_gram in n_grams:
						for b in all_before:
							try:
								b_index=n_gram.index(b[1])
							except:
								b_index=-1
							if b_index!=-1 and b_index>0 and n_gram[b_index-1]==b[0]:
								for a in all_after:
									try:
										a_index=n_gram.index(a[0])
									except:
										a_index=-1
									if a_index!=-1 and b_index+1<a_index:
										# print 'Hi'
										possible_metric=''
										for ind in range(b_index+1,a_index):
											possible_metric+=n_gram[ind]+' '
										possible_metric=possible_metric.rstrip()
										possible_pattern=''
										for ind in range(b_index-1,a_index+1):
											possible_pattern+=n_gram[ind]+' '
										possible_pattern=possible_pattern.rstrip()
										if isNoun(possible_metric,list(n_gram)) == True :
											if True:
												new_metrics.append(possible_metric)
												new_patterns.append(possible_pattern)
												# break
					# b1 = False
					# for n_gram in n_grams:
					# 	for i in n_gram :
					# 		if i in all_before :
					#  			b_index = n_gram.index(i[1])
					# 			for a in all_after:
					# 				try:
					# 					a_index=n_gram.index(a)
					# 				except :
					# 					a_index = -1
					# 				if a_index!=-1 and a_index > b_index + 1:
					# 					possible_metric = ""
					# 					metric_len = 0
					# 					for ind in range(b_index+1,a_index):
					# 						metric_len += 1
					# 						possible_metric += n_gram[ind] +  " "
					# 					possible_metric = possible_metric.rstrip()
					# 					possible_pattern = ""
					# 					for ind in range(b_index,a_index+1):
					# 						possible_pattern += n_gram[ind] +  " "
					# 					possible_pattern = possible_pattern.rstrip()
					# 					if isNoun(possible_metric,list(n_gram)) == True :
					# 						if b_index == 1	:
					# 							b1 = True
					# 							new_metrics.append(possible_metric)
					# 							new_patterns.append(' '.join(n_gram[b_index:a_index+1]))
					# 							break
					# 						if b_index == 0 :
					# 							if b1 == True :
					# 								b1 = False
					# 							else :
					# 								new_metrics.append(possible_metric)
					# 								new_patterns.append(' '.join(n_gram[b_index:a_index+1]))
					# 								break


		except:
			pass
	# print new_metrics
	# print
	metricCount = Counter(new_metrics)
	new_metric_count= Counter()
	for metric in metricCount:
		if metricCount[metric]>0 and len(metric) > 1:
			new_metric_count[metric]=metricCount[metric]
	metricCount=new_metric_count
	patternCount = Counter(new_patterns)
	# print s.most_common(5)
	count = 0
	# for i in metricCount.items():
	# for i in metricCount.most_common(50):
	# for i in patternCount.items():
	# for i in patternCount.most_common(5):
		# count += i[1]
		# print "%s 				%d" %(i[0],i[1])

	# print "Total = %d" % count	
	print "Start the evaluation."
	gold_metrics = pickle.load(open("output_patterns.p"))
	p_num,p_denom,r_num,r_denom = evaluateFromPattern(metricCount,gold_metrics)
	if p_denom == 0 or r_denom == 0:
		prec = 0
		rec = 0
	else :
		prec=float(p_num)/float(p_denom)
		rec=float(r_num)/float(r_denom)
	if rec > 1 :
		rec = 1
	print "%d\t%d\t%d\t%d\t%d\t%d\t%f\t%f\t%f" % (cutoff,len(metricCount.keys()),p_num,p_denom,r_num,r_denom,prec, rec,Hmean(prec,rec))

	# print "%d\t%d\t%f\t%f\t%f" % (cutoff,len(metricCount.keys()),prec, rec,Hmean(prec,rec))
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
		# if top==10 and cutoff==10:
		# 	print metricCount.most_common(top)
		# print "%d\t%d\t%f\t%f\t%f" % (cutoff,top,prec,rec,Hmean(prec,rec))
		print "%d\t%d\t%d\t%d\t%d\t%d\t%f\t%f\t%f" % (cutoff,top,p_num,p_denom,r_num,r_denom,prec, rec,Hmean(prec,rec))		
		# if top <= 10 :
		# 	print metricCount.most_common(top)	
		top -= 5
		
cutoff = 5
print "The values of precison and recall as per the cutoff of training patterns and training outputs"
print "Cutoff 	Top 	Precison 	Recall 	fScore"
for i in range(5):
	bootstrap(["ROUGE","BLEU","DICE","JACCARD"],cutoff)
	# indTrain(["ROUGE","BLEU","DICE","JACCARD"],cutoff)
	cutoff += 5
	# break
# bootstrap(["ROUGE","BLEU","DICE","JACCARD"],0)
	
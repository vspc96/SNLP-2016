import os
import xml.etree.ElementTree as ET
from nltk import ngrams,word_tokenize,pos_tag,sent_tokenize
from nltk.parse import stanford
from collections import Counter



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
	ret = ngrams(text.split(),n)
	return ret

def isNoun(words,text):
	i = 0
	tags = pos_tag(text)
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

def bootstrap(metrics):
	metrics = metrics.lower()
	pdf_folder_test='./rouge/'
	pdf_folder_eval = './RunData/'
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
					patterns=getPatterns(chunk.text.lower(),metrics)
					all_patterns += patterns
		except :
			pass
	count = Counter(all_patterns)
	print len(all_patterns)
	all_after = set()
	all_before = set()
	pattern_tuples = set()
	for i in count.most_common(5):
		k = i[0]
		k = k.split(' ')
		for ek in xrange(len(k)):
			if k[ek] == metrics :
				pattern_tuples.add((k[ek-1],k[ek+1]))	
				try:
					all_before.add(k[ek-1])
				except :
					pass
				try:
					all_after.add(k[ek+1])
				except :
					pass
	count = 0
	max_length_before=getMaxWordLength(all_before)
	max_length_after=getMaxWordLength(all_after)
	metric_length_limit=getMaxWordLength(metrics)+1
	n=max_length_before+max_length_after+metric_length_limit
	new_metrics= []
	new_patterns = []
	xml_files_eval = os.listdir(xml_folder_eval)
	for xml in xml_files_eval:
		count += 1
		try:
			tree=ET.parse(xml_folder_eval+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					n_grams=getNGrams(chunk.text.lower(),n)
					for n_gram in n_grams:
						n_gram = list(n_gram)
						for i in n_gram :
							if i in all_before :
					 			b_index = n_gram.index(i)
								for a in all_after:
									try:
										a_index=n_gram.index(a)
									except :
										a_index = -1
									if a_index!=-1 and a_index > b_index + 1:
										possible_metric = n_gram[b_index+1:a_index]
										if isNoun(possible_metric,n_gram) == True:
											new_metrics.append(possible_metric)
											new_patterns.append(n_gram[b_index:a_index+1])
											

		except:
			pass
	s = Counter([tuple(x) for x in new_metrics])
	s1 = Counter([tuple(x) for x in new_patterns])
	for i in s :
		print i, s[i]
bootstrap("ROUGE")
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
	except :
		pass
	# return before,after,patterns
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

# def isNoun(words,text):
# 	try:
# 		wordlist=words
# 		text=''
# 		for word in wordlist:
# 			if len(word)==0:
# 				continue
# 			text+=word[0].upper()+word[1:]+' '
# 		text=text.strip()
# 		tags = pos_tag(text)
# 		words=words
# 		# print tags
# 		for tag in tags :
# 			for word in words:
# 				if len(tag[0])==0:
# 					continue
# 				if tag[0].lower()==word and tag[1] != 'NNP':
# 					return False
# 		return True
# 	except Exception ,e:
# 		print e
# 		tags = pos_tag(words)
# 		for tag in tags :
# 			if tag[1] != 'NN' and tag[1] != 'NNP':
# 				return False
# 		return True

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
					# before,after,patterns=getPatterns(chunk.text,metrics)
					patterns=getPatterns(chunk.text.lower(),metrics)
					# all_before = all_before.union(before)
					# all_after = all_after.union(after)
					all_patterns += patterns
		except :
			pass
	count = Counter(all_patterns)
	print len(all_patterns)
	# print all_before, all_after
	# print count.most_common(20)
	# all_before = list(all_before)
	# all_after = list(all_after)
	all_after = set()
	all_before = set()
	pattern_tuples = set()
	for i in count.most_common(5):
		k = i[0]
		k = k.split(' ')
		for ek in xrange(len(k)):
			if k[ek] == metrics :
				pattern_tuples.add((k[ek-1],k[ek+1]))	
				for bef in k[:ek] :
					all_before.add(bef)
				for aft in k[ek+1:] :
					all_after.add(aft)
	print pattern_tuples
	count = 0
	# print all_before
	# print all_after
	max_length_before=getMaxWordLength(all_before)
	max_length_after=getMaxWordLength(all_after)
	metric_length_limit=getMaxWordLength(metrics)+1
	n=max_length_before+max_length_after+metric_length_limit
	# n = 6
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
						 		try :
						 			b_index = n_gram.index(i)
								except :
									b_index = -1
								if b_index != -1: 
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
		# if count > 5 :
		# 	break
	# s = set([tuple(x) for x in new_metrics])
	s = Counter([tuple(x) for x in new_metrics])
	s1 = Counter([tuple(x) for x in new_patterns])
	print s1
	print (s)
bootstrap("ROUGE")
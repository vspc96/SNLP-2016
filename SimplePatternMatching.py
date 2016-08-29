import os
import xml.etree.ElementTree as ET
from nltk import ngrams,word_tokenize,pos_tag

def getPatterns(text,metrics):
	before=set()
	after=set()
	try :
		words=text.split(' ')
		n = len(words)
		for i in xrange(n):
			if words[i] == metrics :
				if i>=1:
					before.add(words[i-1])
					print words[i-1]
				if i>=2:
					before.add(words[i-2])
				if i<n-1:
					after.add(words[i+1])
					print words[i+1]
				if i<n-2:
					after.add(words[i+2])
	except :
		pass	
	return before,after

def getNGrams(text,n):
	ret = ngrams(text.split(),n)
	return ret

def isNoun(words,text):
	tags = pos_tag(words)
	# print tags
	for tag in tags :
		if tag[1] != 'NN' and tag[1] != 'NNP':
			return False
	return True

def getMaxWordLength(patterns):
	max_length=0
	for pattern in patterns:
		max_length=max(max_length,len(pattern.split(' ')))
	return max_length

def bootstrap(metrics):
	pdf_folder='./'
	ocr_folder='/var/www/html/OCR++/myproject/media/documents/'
	pdf_files=os.listdir(pdf_folder)
	xml_folder=pdf_folder+ "xmlfiles/"
	# try:
	# 	os.mkdir(xml_folder)
	# except:
	# 	pass
	# for pdf in pdf_files:
	# 	if pdf[-4:]!='.pdf':
	# 		continue
	# 	xml_name=pdf[:-3]+'xml'
	# 	print xml_name
	# 	os.system('cp '+pdf_folder+pdf+' '+ocr_folder+'input.pdf')
	# 	os.system('python '+ocr_folder+'main_script_batch.py')
	# 	os.system('cp '+ocr_folder+'Secmap.xml '+xml_folder+xml_name)

	xml_files=os.listdir(xml_folder)
	all_before=set(' ')
	all_after=set(' ')
	for xml in xml_files:
		try:
			tree=ET.parse(xml_folder+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					before,after=getPatterns(chunk.text,metrics)
					all_before = all_before.union(before)
					all_after = all_after.union(after)
		except :
			pass
	max_length_before=getMaxWordLength(all_before)
	max_length_after=getMaxWordLength(all_after)
	metric_length_limit=getMaxWordLength(metrics)+1
	n=max_length_before+max_length_after+metric_length_limit
	new_metrics= []
	all_before = list(all_before)
	all_after = list(all_after)
	count = 0
	for xml in xml_files:
		print count
		count += 1
		try:
			tree=ET.parse(xml_folder+xml)
			root=tree.getroot()
			for section in root.findall('section'):
				for chunk in section.findall('chunk'):
					n_grams=getNGrams(chunk.text,n)
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

		except:
			pass
		if count > 5 :
			break
	s = set([tuple(x) for x in new_metrics])
	# print s
bootstrap("English")
import os

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


ocr_folder='/var/www/html/OCR++/myproject/media/documents/'
pdf_files=os.listdir("./")
xml_folder = "xml_files/"
getXML(pdf_files,"./",ocr_folder,xml_folder)
	
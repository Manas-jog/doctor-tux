import json
# from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import jsonrpclib
from pprint import pprint
import csv
from tag_extract import TagExtractor
import operator
import nltk


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))



class SemanticMatching:

	nlp = StanfordNLP()
	negative_words=set([])
	tags={}
	synonym_tags={}
	complex_tags={}
	complex_tags_replacements={}
	tge=TagExtractor()

	def __init__(self):
		#print " i am here"
		f=open('sentiment/negative-words.txt','r')
		for line in f:
			line=line.rstrip('\n')
			self.negative_words.add(line)
		#print "negative_words"
		stf = open("Data/tags_synonym.csv", 'r') #converting each tag to its hypernym
		rdr= csv.reader(stf)
		for r in rdr:  
			tmp=r[0].split(';')
			#r[0]=tag  r[1]=tag it should be replaced with
			#print tmp[1]+'#####'+tmp[0]
			self.synonym_tags[tmp[0]]=tmp[1]
		stf.close()

		tf=open("Data/tags.csv", 'r') #assign wieght for tag for each tag
		rdr=csv.reader(tf)
		for r in rdr:
			tmp=r[0].split(';') #tmp[0]=tag      tmp[1]=frequency
			self.tags[tmp[0]]=int(tmp[1])
		tf.close()

		for tmp in self.tags:
			t=tmp.split('-')
			if len(t)>1:
				t2=tmp.replace('-',' ')
				if t[0] not in self.complex_tags:
					self.complex_tags[t[0]]=[]

				self.complex_tags[t[0]].append(t2)
				#self.complex_tags_replacements[t[0]]=tmp
				self.complex_tags_replacements[t2]=tmp

		self.tge.constructor(self.tags,self.complex_tags,self.synonym_tags,self.complex_tags_replacements)

	def getSemanticStruct(self, sentence):
		result = self.nlp.parse(sentence)
		flag=False
		dep_result=result['sentences'][0]['dependencies']
		indexed_result=result['sentences'][0]['indexeddependencies']
		root_word=dep_result[0][2]
		root_index=indexed_result[0][2].split('-')[-1]
		words_json=result['sentences'][0]['words']
		tokens=[]
		key_words=[]
		key_words_index=[]
		neg_words_index=set([])

		#pprint(dep_result)
		key_words.append(root_word)
		key_words_index.append(root_index)

		for w in words_json:
			tokens.append(w[0])
		for i in range(1,len(indexed_result)):
			if root_word in  dep_result[i]:
				#print dep_result[i][2]+'\t'+indexed_result[i][2].split('-')[-1]
				key_words.append(dep_result[i][2])
				key_words_index.append(int(indexed_result[i][2].split('-')[-1]))

				if dep_result[i][0] == u'neg':
					flag=True
					neg_words_index.add(int(indexed_result[i][2].split('-')[-1]))
					if dep_result[i-1][0] == u'aux':
						neg_words_index.add(int(indexed_result[i-1][2].split('-')[-1]))

			for i in neg_words_index:
				for j in range(0, len(key_words)):
					if(i==key_words_index[j]):
						#print str(j)+'###'+str(key_words[j])
						del key_words[j]
						del key_words_index[j]
						break

			for j in range(0,len(key_words)):
				key_words[j]=key_words[j].lower()

		#print key_words
		return (root_word,root_index,tokens,key_words,key_words_index,flag,neg_words_index)

	def batchCalculateStructure(self,titles,sims2):
		#structures=[]
		#distance={}
		#tagListTitle=[]
		if (sims2[0][1]-sims2[1][1]) >0.11:
			return []
		questionsList=[]
		#for title in ques_titles:
		for i in range(0,len(sims2)):
			title=titles[sims2[i][0]]
			(root_word,root_index,tokens,key_words,key_words_index ,flag,neg_words_index)=self.getSemanticStruct(title)
			#structures.append((root_word,root_index,key_words,key_words_index))
			tags_list=[]
			tags_dist={}
			#if flag==False:
			#	for tk in tokens:
			#		if tk in self.negative_words:
			#			flag=True
			#			break
			#	if flag==False:
			#		continue

			key_words=self.tge.identifyComplextags(key_words)
			key_words=self.tge.resolveHyponomy(key_words)
			for j in range(0,len(key_words)):
				kw=key_words[j]
				if kw in self.tags:
					tags_list.append(kw)
					tags_dist[kw]=int(key_words_index[j])

			for val in neg_words_index:
				for td in tags_dist:
				#print td
					if int(tags_dist[td])<int(root_index):
					#print td+"\t"+str(tags_dist[td])
						tags_dist[td]=int(tags_dist[td])+1

			for td in tags_dist:
			#print str(abs(tags_dist[td]-int(root_index)))+"    "+str(abs(tags_dist[td]))
				tags_dist[td]=abs(tags_dist[td]-int(root_index))

			questionsList.append((sims2[i][0],sorted(tags_dist, key=tags_dist.get)))
			#else:

		return questionsList

	def calculateStructure(self,sentence): #0: trouble shooting	#1:direct question
		(root_word,root_index,tokens,key_words,key_words_index ,flag,neg_words_index)=self.getSemanticStruct(sentence)
		tags_list=[]
		tags_dist={}

		#if flag==False:
		#	for tk in tokens:
		#		if tk in self.negative_words:
		#			flag=True
		#			break
		#	if flag==False:
		#		return (1,[])

		key_words=self.tge.identifyComplextags(key_words)
		key_words=self.tge.resolveHyponomy(key_words)

		for j in range(0,len(key_words)):
			kw=key_words[j]
			if kw in self.tags:
				tags_list.append(kw)
				tags_dist[kw]=int(key_words_index[j])


		#tags_dist=sorted(tags_dist.iteritems(), key=operator.itemgetter(1))
		#print "root index:"+str(root_index)
		for val in neg_words_index:
			for td in tags_dist:
				#print td
				if int(tags_dist[td])<int(root_index):
					#print td+"\t"+str(tags_dist[td])
					tags_dist[td]=int(tags_dist[td])+1
				#elif tags_dist[td]>root_index:
				#	tags_dist[td]=int(tags_dist[td])-1

		for td in tags_dist:
			#print str(abs(tags_dist[td]-int(root_index)))+"    "+str(abs(tags_dist[td]))
			tags_dist[td]=abs(tags_dist[td]-int(root_index))

		return(0,sorted(tags_dist, key=tags_dist.get))

	def identifyClosestQuestion(self,sentence,titles,sims2, answers):
		sent_tags=self.calculateStructure(sentence)
		ques_tags_list=self.batchCalculateStructure(titles,sims2)
		new_ques_list=[]
		if (sent_tags[0]==1) or (len(ques_tags_list)==0):
			print "using only tfidf"
			print "Similar Question: "+titles[sims2[0][0]]
			print "********Answer************"
			print nltk.clean_html(answers[sims2[0][0]])
			return sims2[0][0]

		#print sent_tags	[1]
		for i in range(0,len(sent_tags[1])):
			new_ques_list=[]
			for qpair in ques_tags_list:
				if(i>=len(qpair[1])):
					continue
				if qpair[1][i]==sent_tags[1][i]:
					new_ques_list.append(qpair)

			if len(new_ques_list)==1:
				print "using parsing"
				print "Similar Question: "+titles[new_ques_list[0][0]]
				print "********Answer************"
				print nltk.clean_html(answers[new_ques_list[0][0]])
				return new_ques_list[0][0]
			if len(new_ques_list)==0:
				print "len is 0"
				new_ques_list=ques_tags_list

			ques_tags_list=new_ques_list

		print "using parsing and tfidf "+ str(i)+"   "+str(len(sims2))
		print "Similar Question: "+titles[new_ques_list[0][0]]
		print "********Answer************"
		print nltk.clean_html(answers[new_ques_list[0][0]])
		return new_ques_list[0][0]




#sm=SemanticMatching()
#print sm.calculateStructure("My headphones don't work on Ubuntu#12.04.")
#print sm.calculateStructure("How do I install Ubuntu#12.04?")
#print sm.calculateStructure("Ubuntu fails to recognize my headphones")
#print sm.calculateStructure("On Ubuntu#12.04 I cannot install RhythmBox.")
#print sm.calculateStructure("I am unable to boot into Ubuntu after installing windows.")
#print sm.calculateStructure("My USB-drive does not work on Ubuntu.")
#print sm.calculateStructure("USB-drive isn't working.")

#question_titles=["My headphones don't work on Ubuntu#12.04.",
#				 "How do I install Ubuntu#12.04?",
#				 "Ubuntu fails to recognize my headphones",
#				 "On Ubuntu I cannot install Rhythm-Box.",
#				 "My USB-drive does not work on Ubuntu.",
#				 "USB-drive isn't working."
#				]

#sims2=[(5,12),(4,10),(0,3),(1,1),(2,2),(3,1)]
#question="I have a problem with my USB-drive on Ubuntu."
#sm.identifyClosestQuestion(question,question_titles,sims2)

#sims2=[(1,30),(0,25),(2,2),(3,1),(5,12),(4,10)]
#question="I have a problem with my headphones on Ubuntu#12.04."
#sm.identifyClosestQuestion(question,question_titles,sims2)

#print sm.batchCalculateStructure(question_titles,sims2)


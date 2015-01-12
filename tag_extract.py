#
# author: Bijil Abraham Philip
#

import nltk
import csv

class TagExtractor:
	tags={} #set of tags
	complex_tags={} #first word of complex tag : complex tag.......complex tag is one having >1 word and seperated by a -
	hyponomy_tags={} #tag: highest level of abstraction/ tag synonym
	complex_tags_replacements={} #first word:complex tag (words seperated by a dash)

	def constructor(self,tags,complex_tags,hyponomy_tags,complex_tags_replacements):
		self.tags=tags
		self.complex_tags=complex_tags
		self.complex_tags_replacements=complex_tags_replacements
		self.hyponomy_tags=hyponomy_tags


	def identifyComplextags(self,features): #wrong implementation
		#features=nltk.word_tokenize(question)
		for i in range(0,len(features)):
			f=features[i]
			if features[i] in self.complex_tags:
				#print self.complex_tags[f]
				#question=question.replace(self.complex_tags[f],self.complex_tags_replacements[f])
				for j in range(0,len(self.complex_tags[f])):
					#print ctag
					ctag=self.complex_tags[f][j]
					if ctag==f:
						features[i]=self.complex_tags_replacements[ctag]

		return features

	def resolveHyponomy(self,features): #convert tags to simplest tags
		#features=question.split()
		for i in range(0,len(features)):
			if features[i] in self.hyponomy_tags:
				#print self.hyponomy_tags[f]
				features[i]=self.hyponomy_tags[features[i]]
		return features

	def getTagsFromQuestion(self,questions):
		features=questions.split()
		tagList=[]
		for f in features:
			if f in self.tags:
				tagList.append(f)

		return tagList

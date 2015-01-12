import nltk
import re
import string

class TransformQuery:

	def give(self, question):
		stopwords = nltk.corpus.stopwords.words('english')
		question_l = question.lower()
		postags = nltk.pos_tag(nltk.word_tokenize(question_l))
		question_l_split = question_l.split(' ')

		for stopword in stopwords:
			for i in xrange(0, len(question_l_split)):
				if stopword == question_l_split[i]:
					question_l_split[i] = ''
					break

			question_l = ' '.join(question_l_split)
			question_l = re.sub('\s+', ' ', question_l)	
		
		tokens = nltk.word_tokenize(question_l)
		importantPOStags = [
			'NN', 'PRP', 'CD', 'FW', 'NNS', 'NNP',
			'NNPS', 'PRP$', 'RB', 'SYM', 'VB',
			'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'
		]

		bagofwordsquery = ''

		for token in tokens:
			tag = ''
			for postag in postags:
				if postag[0] in token:
					tag = postag[1]
					if tag in importantPOStags:
						bagofwordsquery += token + ' '
					break

		return bagofwordsquery.translate(string.maketrans("", ""), string.punctuation)



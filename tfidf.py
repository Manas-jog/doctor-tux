from gensim import corpora, models, similarities
from nltk.tokenize.punkt import PunktWordTokenizer
from querytransformer import TransformQuery
from semantic_matching import SemanticMatching

class BagOfWords:

	def __init__(self):
		self.collections = []
		self.dictionaries = []
		self.times = 0

	#you can call this function many times, and it'll store stuff parallely!

	def processRawText(self, filename):
		iF = open(filename, 'r')
		documents = []

		tokenizer = PunktWordTokenizer()

		for line in iF:
			document = line.rstrip().lower()
			title = unicode(document, 'utf-8')
			tokens = tokenizer.tokenize(title)
			
			if len(tokens) == 0:
				tokens = [u'null']

			documents.append(tokens)
			
		self.collections.append(documents)

		dictionary = corpora.Dictionary(documents)
		self.dictionaries.append(dictionary)
		dictionary.save('temp/BagOfWords' + str(self.times + 1) + '.syms')

		corpus = [dictionary.doc2bow(doc) for doc in documents]
		corpora.MmCorpus.serialize('temp/BagOfWords' + str(self.times + 1) + '.corpus', corpus)

		self.times += 1


	def initModels(self):

		for i in xrange(0, len(self.collections)):

			#load corpus
			corpus = corpora.MmCorpus('temp/BagOfWords' + str(i + 1) + '.corpus')
			tfidfModel = models.tfidfmodel.TfidfModel(corpus)
			tfidfModel.save('models/tfidf' + str(i + 1) + '.model')

			#initialize similarity indexing file
			index = similarities.Similarity('temp' + str(i + 1) + '/sim', tfidfModel[corpus], len(self.dictionaries[i]))
			index.save('temp/similarities' + str(i + 1))

			print 'learnt tfidf for collection #', i


	def search(self, titles):
		N = 2

		self.corpusCollection = []
		self.models = []
		self.indices = []

		for i in xrange(0, N):
			corpus = corpora.MmCorpus('temp/BagOfWords' + str(i + 1) + '.corpus')
			print 'got corpus for', i
		
			dictionary = None

			if len(self.dictionaries) != len(self.collections) - 1:
				dictionary = corpora.Dictionary.load('temp/BagOfWords' + str(i + 1) + '.syms')
				self.dictionaries.append(dictionary)
				print 'got dict for', i
			else:
				dictionary = self.dictionaries[i]

			self.corpusCollection.append(corpus)
			model = models.tfidfmodel.TfidfModel.load('models/tfidf' + str(i + 1) + '.model')
			index = similarities.Similarity.load('temp/similarities' + str(i + 1))
			self.models.append(model)
			self.indices.append(index)

		
		sm=SemanticMatching()

		while True:
			finalsims = []
			debug = []

			for i in xrange(0, len(titles)):
				finalsims.append(float(0))
				debug.append([])

			print 'New Query:'
			query = raw_input()
			pure_query = query
			query = TransformQuery().give(query)
			print 'Query rewritten to:', query

			if len(query) < 2:
				break

			doc = query

			for i in xrange(0, N):
				vec_bow = self.dictionaries[i].doc2bow(doc.lower().split())
				vec_model = self.models[i][vec_bow]
				sims = self.indices[i][vec_model]
				simsCpy = list(enumerate(sims))
				
				#add all similarities
				for j in xrange(0, len(simsCpy)):
					key, value = simsCpy[j]
					finalsims[j] += value
					debug[j].append(value)
					
			results = []
			for i in xrange(0, len(finalsims)):
				result = i, finalsims[i]
				results.append(result)

			sims2 = sorted(results, key=lambda item: -item[1])
			sims_new=[]
			for j in xrange(0,20):
				sims_new.append(sims2[j])
				print 'TFIDF(', j, '):', titles[sims2[j][0]], '{', sims2[j][1], '}'

			answers = []
			aF = open('Data/answers.txt', 'r')
			
			for line in aF:
				answers.append(line.rstrip())

			print '-------x-x-x-x-x-x------------'
			sm.identifyClosestQuestion(pure_query,titles,sims_new, answers)
			print '##############################'
			#for j in xrange(0, 20):
			#	tup = sims2[j]
			#	key = tup[0]
			#	print titles[key], debug[key]
			#	print '---Enter to continue [ENTER]:'
			#	raw_input()


def main():
	titles = []
	iF = open('Data/questionsTitles.txt', 'r')

	for line in iF:
		titles.append(line.rstrip())

	approach = BagOfWords()
	#approach.processRawText('Data/questionsTexts.txt')
	#approach.processRawText('Data/questionsTitles.txt')
	#approach.initModels()

	approach.search(titles)

main()

from src.utils.normalize import normalize_and_remove_stop_words
from src.featurizers import skipthoughts
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

def gen_vocab(corpus_dict, vocab=1000, **kwargs):
    '''
    Generates a dictionary of words to be used as the vocabulary in features that utilize bag of words.
    
    Args:
        corpus_dict (OrderedDict): An ordered list of the most frequently occurring tokens in the corpus
        vocab_size (int): the number of words to be used in the vocabulary 
        
    Returns:
        dict: a dictionary of size vocab_size that contains the most frequent normalized and non-stop words in the corpus
    '''
    index = 0
    vocabdict = dict()
    for word in corpus_dict:
        if len(vocabdict) < vocab:
            cleantext = normalize_and_remove_stop_words(word)
            if cleantext != '':
                if not cleantext in vocabdict:
                    vocabdict[cleantext] = index
                    index+=1
        else: break
    return vocabdict

def build_lda(trainingdata, vocabdict, topics=40, **kwargs):
    '''
    Fits a LDA topic model based on the corpus vocabulary.
    
    Args:
        trainingdata (list): A list containing the corpus as parsed JSON text 
        vocabdict (dict): A dictionary containing the vocabulary to be used in the LDA model
        topics (int): the number of topics to be used in the LDA model
        
    Returns:
        LatentDirichletAllocation: A LDA model fit to the training data and corpus vocabulary
    '''
   
    vectorizer = CountVectorizer(analyzer = "word", vocabulary = vocabdict)
    trainingdocs = []
    
    for entry in trainingdata: trainingdocs.append(entry['body_text'])
    trainingvectors = vectorizer.transform(trainingdocs)
    
    lda = LatentDirichletAllocation(n_topics=topics, random_state=0)
    lda.fit(trainingvectors)
    return lda

def main(argv):
    '''
    Controls the preprocessing of the corpus, including building vocabulary and model creation.
    
    Args:
        argv (list): contains a list of the command line features, a dictionary of all tokens in the corpus, an array of parsed JSON documents, a list of the command line parameters
    
    Returns:
        multiple: dictionary of the corpus vocabulary, skipthoughts encoder_decoder, trained LDA model
    '''
 
    features, corpus_dict, trainingdata = argv
    encoder_decoder = None
    vocab= None
    lda = None
    
    if 'st' in features: encoder_decoder = skipthoughts.load_model()
    
    if 'bow' in features: vocab = gen_vocab(corpus_dict, **features['bow'])
    elif 'lda' in features: vocab = gen_vocab(corpus_dict, **features['lda'])
    if 'lda' in features: lda = build_lda(trainingdata, vocab, **features['lda'])
        
    return vocab, encoder_decoder, lda

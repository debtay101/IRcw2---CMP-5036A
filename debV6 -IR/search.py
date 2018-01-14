#! /usr/bin/python
import re
import ast
import math
import collections


def openFile(file):
    openFile = 0
    with open(file) as data:
        # ast.literal_eval is useful if you expected a list (or something similar) by the user.
        # source https://stackoverflow.com/questions/29552950/when-to-use-ast-literal-eval
        openFile = ast.literal_eval(data.read())
    return openFile


def main():
    # use cosine to check similarities
    def cosineSimilarity(docID, query):
        sumaa, sumbb, sumab = 0, 0, 0
        for word in vocab:
            if (word in TFIDF[docID]):
                # dot product = Cartesian coordinates of two vectors
                dotfidf = TFIDF[docID][word]
            else:
                # if not found, 0 for dot product
                dotfidf = 0
            if (word in query):
                fidf = normalisation[word]
            else:
                # cosine similarity
                fidf = 0

            # Calculate cosine similarity - use sum function
            a = dotfidf
            b = fidf
            sumaa += a * a
            sumbb += b * b
            sumab += a * b

        sumaa = math.sqrt(sumaa)
        sumbb = math.sqrt(sumbb)
        if (sumaa == 0):
            return 0
        if (sumbb == 0):
            return 0
        return sumab / (sumaa * sumbb)


    # TFIDF for Normalisation
    normalisation = {}
    # Document vectors dictionary
    documentVectors = {}
    from collections import OrderedDict

    vocab = openFile("vocab.txt")
    TFIDF = openFile("tfidf.txt")
    postings = openFile("postings.txt")

    # convert tfidf to ints to enable data to get ratings at the end
    tfidf_ints = {}
    for a, b in TFIDF.items():
        tfidf_ints[int(a)] = b
    TFIDF = tfidf_ints
    #delete the variable
    del tfidf_ints

    # idf dictionary
    idf = dict.fromkeys(postings)
    # termFrequency dictionary
    termFrequency = dict.fromkeys(postings)
    # collection frequency dictionary
    collectionFrequency = dict.fromkeys(vocab)
    # docIDS dictionary
    docIDdictionary = {}
    # build url array from docids
    urlList = openFile("docids.txt")

    for x in postings:
        temporary = postings[x][len(postings[x]) - 1]
        temporary = temporary.split(':')
        idf[x] = temporary[1]
        collectionFrequency[x] = vocab[x]
        termFrequency[x] = postings[x]
        termFrequency[x].pop(len(postings[x]) - 1)

    for word in termFrequency:
        temporaryDictionary = dict()
        for value in termFrequency[word]:
            docID = re.findall(r"(\d*):", str(value))[0]
            termFreq = re.findall(r":(\d*)", str(value))[0]
            temporaryDictionary[docID] = termFreq
            termFrequency[word] = temporaryDictionary

    for word in postings:
        docID = re.findall(r"(\d*):", str(postings[word]))
        docID = [int(d) for d in docID]
        docIDdictionary[word] = docID

    print('')
    # User enters question and allow questions to be read as lower case so they can match against dictionaries
    word = input('Enter your question: ')
    word = re.sub(r'[^\w]', ' ', word)
    word = word.lower()

    # use nltk lemmatizer to enable stopwords to be used
    import nltk
    lemma = nltk.stem.wordnet.WordNetLemmatizer()

    question = word.split()

    stopwords = ['i', 'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'com', 'do', 'from', 'how', 'in', 'is', 'it',
                    'of', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 'when', 'where', 'who', 'will', 'with','www']

    for word in question:
        flag = False
        if (word in stopwords):
            flag = True
            question.remove(word)
        else:
            flag = False

    documents = []
    cosine = {}

    for word in question:
        print('')
        print('  ANSWER: ', word)

        if (word not in termFrequency):
            print(type(termFrequency))
            print('Not found')
        else:
            print('Document Frequency: ', idf[word])
            print('Collection Frequency: ', str(vocab[word]))

            tfWord = (1 / len(question))
            idfWord = (math.log10(len(urlList) / int(idf[word])))
            tfidfQuery = tfWord * idfWord
            normalisation[word] = tfidfQuery
            print('')

            # documents = relative documents for Ranked list
            # use both documents and docIDs dictionary to help identify the ranking order
            documents = list(set(documents + docIDdictionary[word]))

    for docid in documents:
        cosine[docid] = cosineSimilarity(docid, question)

    #Rank in order using the cosine dot product data and python list ordering (sorted) process
    orderedCosines = OrderedDict(sorted(cosine.items(), key=lambda t: t[1],reverse=True))

    # Order the Cosine Similarities for the URLs. Build ordered URL list highest priority at top
    print('Ordered list of URLs:')
    for a, b in list(orderedCosines.items())[:20]:
        # use '' to add a space between the rating and URL
        print(b, '', urlList[a])

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()


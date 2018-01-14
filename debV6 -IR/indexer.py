#! /usr/bin/python

import math
import re
import traceback
import datetime

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = {}
# document frequency dictionary
documentFrequencies = {}
# termFrequencies dictionary
termFrequencies = {}


def main():
    # one off single page .txt file - use for testing
    infile = 'testPage.txt'
    textin = open(infile, 'rU')
    page_contents = textin.read()
    textin.close()


# writes indexes when PCcrawler run
def write_index():
    # global variable references
    global docids
    global postings
    global vocab
    # for tfidf .txt file for use later
    global tfidf
    # for test page
    global testPage

    # adds documentFrequencies to postings
    for word in postings:
        postings[word].append(
            'document Frequency: ' + str(documentFrequencies[word]))

    # pull idf frequency from postings
    # used fromkeys() : builds new dictionary with keys from seq and values set.
    # Source: https://www.tutorialspoint.com/python/dictionary_fromkeys.htm
    idf = dict.fromkeys(postings)  # idf dictionary is from the postings file

    for x in postings:
        temp = postings[x][len(postings[x]) - 1]
        # splits on colon
        temp = temp.split(':')
        # get document Frequency
        idf[x] = temp[1]

    # Calculate TF*IDF
    document = {}
    for docid in termFrequencies:
        TFIDF = {}
        # word count for each word
        wordCount = 0
        for word in termFrequencies[docid]:
            wordCount += termFrequencies[docid][word]
        # total word count for document
        for word in termFrequencies[docid]:
            TF = (1 + math.log(float(termFrequencies[docid][word]), 10))
            IDF = (math.log10(len(docids) / int(idf[word])))
            TFIDF[word] = TF * IDF
        document[docid] = TFIDF

    # write to index files: docids, vocab, postings, tfidf, testPage and
    # lemmatize
    outlist1 = open('docids.txt', 'w')
    outlist2 = open('vocab.txt', 'w')
    outlist3 = open('postings.txt', 'w')
    outlist4 = open('tfidf.txt', 'w')
    outlist5 = open('testPage.txt', 'w')
    outlist6 = open('lemmatize.txt', 'w')

    print(docids, file=outlist1)
    print(vocab, file=outlist2)
    print(postings, file=outlist3)
    print(document, file=outlist4)
    print(document, file=outlist5)
    print(document, file=outlist6)

    outlist1.close()
    outlist2.close()
    outlist3.close()
    outlist4.close()
    outlist5.close()
    outlist6.close()

    return


def make_index(url, page_contents):  # the main indexing function
    # declare refs to global variables
    global docids
    global postings
    global vocab

    if isinstance(page_contents, bytes):
        # convert bytes to string if necessary
        # If any data has corrupted, we get an error occur.
        try:
            clean = page_contents.decode('utf-8')
        except Exception as ex:
            error = ''.join(traceback.format_exception_only(type(ex), ex))
            error = error.replace('\n', '')
            print(f'ERROR decoding {url}. I am gonna append this to errors.txt'
                  ' so you can retry it again.')
            with open('errors.txt', 'a+') as error_list:
                time_string = str(datetime.datetime.now())
                error_line = f'{time_string} - {error} - {url}\n'
                error_list.write(error_line)
            return

    else:
        clean = page_contents
    if isinstance(clean, bytes):
        print('!!!ERROR!!! page not converted to string')

    # Use REGEX to get rid of data (clean it up)
    # Use re.sub (pattern, repl, string[, count, flags])
    # Return the string obtained by replacing the leftmost non-overlapping occurrences of pattern in
    # string by the replacement repl. If the pattern isn’t found, string is returned unchanged.
    # re.sub explanation above found on https://docs.python.org/3.1/library/re.html#re.sub

    # Completed by trial and error eg add a regex option, run file & see what happens
    # Order of process below also trial and error.  ------
    # Changed slightly from CW1 as found more efficient regex code

    # remove scripts
    clean = re.sub('<script.*?script>', ' ', clean, flags=re.DOTALL)
    # remove CDATA ?redundant
    clean = re.sub('<!\[CDATA\[.*?\]\]', ' ', clean, flags=re.DOTALL)
    # remove links - part 1
    clean = re.sub('<link.*?link>|<link.*?>', ' ', clean, flags=re.DOTALL)
    # remove links - part 2
    clean = re.sub('<style.*?style>', ' ', clean, flags=re.DOTALL)
    # remove newlines, tabs
    clean = re.sub('\\\\n|\\\\r|\\\\t', ' ', clean)
    # change \' to '
    clean = re.sub('\\\\\'', '\'', clean)
    # remove HTML tags
    clean = re.sub('<.*?>', ' ', clean, flags=re.DOTALL)
    # remove stray JS
    clean = re.sub('{.*?}', ' ', clean)
    # remove hex values
    clean = re.sub('\\\\x..', ' ', clean)
    # remove comments
    clean = re.sub('<--|-->', ' ', clean, flags=re.DOTALL)
    # remove stray angle brackets
    clean = re.sub('<|>', ' ', clean)
    # remove HTML entities
    clean = re.sub('&.*?;|#.*?;', ' ', clean)
    # remove punctuation and replace with ' '
    clean = re.sub(r'[^\w]', ' ', clean)

    # replace multiple spaces with single one
    page_text = re.sub('\s+', ' ', clean)
    # change text to lower case
    page_text = page_text.lower()

    print('url = ', url)

    # remove https://
    if re.search('https:..', url):
        domain_url = re.sub('https://', '', url)
    # remove http://
    elif re.search('http:..', url):
        domain_url = re.sub('http://', '', url)
    else:
        print("No match for url=", url)

    # remove www.
    if re.search('www.', domain_url):
        domain_url = re.sub('www.', '', domain_url)

    ### add url to list of documents
    # return if already found
    if domain_url in docids:
        return
    else:
        # add url to docids table
        docids.append(domain_url)
        # get string version of docid
        docid = str(docids.index(domain_url))

        ##### stemming and other processing goes here #####
        # lemmatize using NLTK instead of UEAlite. UEAlite kept erroring so had to use NLTK
        import nltk
        from nltk.corpus import wordnet
        lemma = nltk.stem.wordnet.WordNetLemmatizer()
        lemmatized = [lemma.lemmatize(page) for page in page_text]
        # build lemmatize.txt file - to show what has been lemmatized
        lemmatized = [lemma.lemmatize("")]

    stopwords = ['i', 'a', 'about', 'an', 'and', 'are', 'as', 'at', 'be', 'by',
                 'com', 'for', 'from', 'how', 'in', 'is',
                 'it', 'of', 'or', 'that', 'the', 'this', 'to', 'was', 'what',
                 'when', 'where', 'who', 'will', 'with',
                 'www']

    # page_text changed to words
    words = page_text
    # local dictionary for term frequencies
    frequency = {}

    for word in words.split():
        if (word in frequency):
            # if word is already in vocab.txt + 1 to term frequency
            frequency[word] += 1
        else:
            frequency[word] = 1

    # add frequency to termFrequencies dictionary
    termFrequencies[docid] = frequency

    # add the vocab counts and postings
    for word in words.split():
        if (word in vocab):
            # if word already in vocab.txt add 1 to term frequency
            vocab[word] += 1
        else:
            # if word not in vocab.txt, add word and add 1 to term frequency
            vocab[word] = 1
        if (not word in postings):
            documentFrequencies[word] = 1
            # add frequency 1 to posting
            postings[word] = [docid + ':' + str(frequency[word])]
        elif (docid not in re.findall(r"(\d*):", str(postings[word]))):
            # check if docid matches current docid
            documentFrequencies[word] += 1
            # if it does then extract frequency and frequency++
            postings[word].append(docid + ':' + str(frequency[word]))

    return


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()

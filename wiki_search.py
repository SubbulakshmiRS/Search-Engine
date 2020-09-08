import glob
import time
import sys
import nltk
import Stemmer
import numpy as np
import re
import operator
# nltk.download('stopwords')
from nltk.corpus import stopwords

class TextProcessor():
    def __init__(self):
        self.stemer = Stemmer.Stemmer('english')
        self.storeStem = {}
        self.stop_words = set(stopwords.words('english')) 
        self.count = 0

    def removePunctiotion(self, text):
        res = re.sub(r'[^\w\s]', ' ', text)
        return res

    def tokenize(self, text):
        text = text.replace("'", " ").replace("_", " ")
        tokens = re.findall(r"[\w']{3,}", text)
        return tokens

    def removeStopwords(self, tokens):
        filtered_tokens = []
        for token in tokens: 
            s = re.sub(r'[^\x00-\x7f]',r' ',token)
            if (s == token) and token not in self.stop_words:
                filtered_tokens.append(token)
        return filtered_tokens

    def stem(self, text):
        stemmedWord = []
        for word in text:
            if word not in self.storeStem:
                # storeStem[word] = self.englishStemmer.stem(word)
                self.storeStem[word] = self.stemer.stemWord(word)
            stemmedWord.append(self.storeStem[word])
        
        if len(self.storeStem)>1000000:
            l = list(self.storeStem.keys())
            m = l[0:100000]
            for dword in m:
                del self.storeStem[dword]
        return stemmedWord

    def processText(self, text):
        textP = self.removePunctiotion(text)
        textP = textP.lower()
        temp = self.stem(self.removeStopwords(self.tokenize(textP)))
        tokenFinal = []
        for word in temp:
            word = word.strip()
            if word == '':
                continue
            else :
                tokenFinal.append(word)
        return tokenFinal

class Search():
    def __init__(self, outputdir):
        self.outputdir = outputdir
        self.k = 0
        self.searchPostList={}
        self.titlesNet = []
        self.docScore = {}
        self.weights = [2,1,1,1,1,1]
        self.types = ["t", "i", "c", "b","r","l"]
        self.textproc = TextProcessor()

        self.getTitles()

    def getTitles(self):
        titlefile = str(self.outputdir + "/title.txt")
        f = open(titlefile,"r")
        self.titlesNet = f.readlines()
        f.close()

    def findIndexFile(self, word):
        self.indexfile = str(self.outputdir+"/INDEX.txt")
        f = open(self.indexfile,"r")
        line = f.readline()
        while line:
            if ":" in line and "|" in line:
                lesserLimit = line.split(":",1)[0]
                lesserLimit = lesserLimit.strip()
                largerLimit = line.split(":",1)[1].split("|",1)[0]
                largerLimit = largerLimit.strip()
                outputfile = line.split(":",1)[1].split("|",1)[1]
                outputfile = outputfile.strip()
                if(word >= lesserLimit and word<=largerLimit):
                    f.close()
                    return outputfile
                line = f.readline()
        f.close()
        return ""

    def extractWord(self, line, start):
        if ":" in line:
            if start:
                word =  line.split(':',1)[0].rsplit('|',1)[-1].strip()
                postlist = line.split(':',1)[1].strip()
                return word, postlist, False
            else:
                word = ""
                postlist = line.split(':',1)[0].rsplit('|',1)[0]
                return word, postlist, True
        else :
            word = ""
            postlist += line.strip()
            return word, postlist, False

    def searchOutputFile(self, outputfile, searchWord, tag):
        f = open(outputfile,"r")
        line = f.readline()
        while line:
            fpos = f.tell()
            word, postlist, t = self.extractWord(line, True)
            while(1):
                fpos = f.tell()
                line = f.readline()
                if(line == ""):
                    f.close()
                    return {}
                w, p, end = self.extractWord(line, False)
                word += w
                postlist += p
                if end:
                    f.seek(fpos)
                    break
            if(word == searchWord):
                f.close()
                return self.extractOccurences(postlist, tag)
            line = f.readline()
        f.close()
        return {}

    def extractOccurences(self, postlist, tag):
        posts = postlist.split("|")
        compare = "d(\d+)"
        occ = {}
        for char in self.types:
            compare += char+"(\d+)"

        for post in posts:
            c = re.compile(compare)
            s = c.search(post)
            if s:
                docID = int(s.group(1))
                pos = int(self.types.index(tag))
                if int(s.group(1+pos)) > 0:
                    if docID not in occ:
                        occ[docID] = 0
                    for i in range(6):
                        if i == pos:
                            occ[docID] += 2*int(s.group(i+2))*self.weights[i]
                        else :
                            occ[docID] += int(s.group(i+2))*self.weights[i]
        return occ
                    
    def processQuery(self, query):
        self.k = int(query.split(',',1)[0])
        self.searchPostList = {}
        plist = query.split(',', 1)[1]
        for char in self.types:
            i = char+":"
            if i in plist:
                temp = plist.split(i)[-1]
                if ":" in temp:
                    self.searchPostList[char]=self.textproc.processText(temp.split(":")[0][:-1])
                else :
                    self.searchPostList[char]=self.textproc.processText(temp)
            else :
                self.searchPostList[char] = []
    
    def searchQuery(self):
        start = 0
        self.docScore = {}
        for tag, lst in self.searchPostList.items():
            if len(lst) == 0:
                continue
            
            if start == 0:
                outputfile = self.findIndexFile(lst[0])
                self.docScore = self.searchOutputFile(outputfile, lst[0], tag)
                common_keys = set(self.docScore.keys())
                start = 1
                temp = lst
                lst = temp[1:]

            for word in lst:
                outputfile = self.findIndexFile(word)
                #scores are of form {docID:[addition of dot product of vector of size 6 and its weights]}
                scores = self.searchOutputFile(outputfile, word, tag)
                common_keys.intersection_update(set(scores.keys()))
                for key in self.docScore:
                    if key in common_keys:
                        self.docScore[key] += scores[key]
                    else :
                        del self.docScore[key]

        print("the complete interference match for all words and tags\n")
        print(self.docScore)
        print("===============================================")
        print("the top k")
        i = 0
        for key in sorted(self.docScore.items(), key=operator.itemgetter(1), reverse=True):
            print(str(key)+" , "+self.titlesNet[key])
            i += 1
            if i >= self.k:
                break
        

if __name__ == "__main__":
    start_time = time.time()
    searchproc = Search(sys.argv[1])

    f = open(sys.argv[2],"r")
    line = f.readline()
    while line:
        startt = time.time()
        searchproc.processQuery(line)
        searchproc.searchQuery()
        tt = time.time()-startt
        print("time taken for this search: "+str(tt)+"\n")
        line = f.readline()

    time_taken = time.time() - start_time
    print("time taken for compelete searching: "+str(time_taken)+"\n")
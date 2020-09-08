import sys
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
from xml import sax
import glob
import re
import nltk
import os
from nltk.corpus import stopwords 
# from nltk.tokenize import word_tokenize
# import nltk.stem as stemmer
import Stemmer
# from nltk.stem import PorterStemmer
# from nltk.stem import LancasterStemmer
from nltk.stem.snowball import SnowballStemmer
import time
import resource

class CreateStatFile():
    def __init__(self, outputdir, statfile, words):
        self.statfile = statfile
        self.outputdir = outputdir
        self.words = words
        self.size, self.num = self.findSizeAndNum()

        self.writeStat()

    def writeStat(self):
        f = open(self.statfile, "a+")
        f.write(str(self.size)+"\n")
        f.write(str(self.num)+"\n")
        f.write(str(self.words)+"\n\n")
        f.close()

    def findSizeAndNum(self):
        total = 0
        num = 0
        try:
            for entry in os.scandir(self.outputdir):
                if entry.is_file():
                    total += entry.stat().st_size
                    num += 1
        except NotADirectoryError:
            return os.path.getsize(self.outputdir), 0
        except PermissionError:
            return 0, 0
        return total, num

class TextProcessor():
    def __init__(self, outputdir, statfile, iter):
        self.outputdir = outputdir
        self.statfile = statfile
        self.iter = iter

        self.createOutputDir()
        # porter = PorterStemmer()
        # lancaster=LancasterStemmer()
        self.stemer = Stemmer.Stemmer('english')
        # self.englishStemmer=SnowballStemmer("english")
        self.wCount = {}
        self.storeStem = {}
        self.max = int(int(resource.getrlimit(resource.RLIMIT_NOFILE)[0])/2)
        if self.max < 1 :
            self.max = 200
        self.stop_words = set(stopwords.words('english')) 
        self.wStr = {}
        self.curDocID = 0
        self.docID = 0
        self.count = 0

    def removePunctuation(self, text):
        res = re.sub(r'[^\w\s]', ' ', text)
        return res

    def tokenize(self, text):
        text = text.replace("'", " ").replace("_", " ")
        tokens = re.findall(r"[\w']{3,}", text)
        return tokens

    def removeStopwords(self, tokens):
        filtered_tokens = []
        for token in tokens: 
            s = re.sub(r'[^\x00-\x7f]',r'',token)
            if (s == token) and s not in self.stop_words:
                s = s.lstrip('0')
                if s == "":
                    s = "0"
                filtered_tokens.append(s)
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

    def processText(self, text, tag, docId):
        self.docID =docId
        textP = self.removePunctuation(text)
        textP = textP.lower()
        textFinal = self.stem(self.removeStopwords(self.tokenize(textP)))
        for word in textFinal:
            word = word.strip()
            if word == '':
                continue
            self.count += 1
            if word not in self.wCount:
                self.wCount[word] = [0,0,0,0,0,0]
            if tag == "title":
                self.wCount[word][0] += 1
            elif tag == "infobox":
                self.wCount[word][1] += 1
            elif tag == "references":
                self.wCount[word][2] += 1
            elif tag == "externallink":
                self.wCount[word][3] += 1
            elif tag == "categories":
                self.wCount[word][4] += 1
            elif tag == "body":
                self.wCount[word][5] += 1

    def createOutputDir(self):
        try:
            os.mkdir(self.outputdir) 
        except FileExistsError:
            pass

    def createIndex(self):
        for word in sorted(self.wCount):
            temp = ""
            temp += ("n"+str(self.iter))
            temp += ("d"+str(self.docID))
            temp += ("t"+str(self.wCount[word][0]))
            temp += ("i"+str(self.wCount[word][1]))
            temp += ("r"+str(self.wCount[word][2]))
            temp += ("e"+str(self.wCount[word][3]))
            temp += ("c"+str(self.wCount[word][4]))
            temp += ("b"+str(self.wCount[word][5]))
            temp += "|"
            if word not in self.wStr:
                self.wStr[word] = temp
            else :
                self.wStr[word] += temp
        self.wCount.clear()
        if self.docID >= (self.curDocID+1)*self.max:
            self.writeIndex()

    def writeIndex(self):
        f = open(self.outputdir + "/"+ str(self.curDocID)+"-"+ str(self.iter)+".txt","w+")
        for word in sorted(self.wStr):
            temp = str(word)
            temp += ":"
            temp += str(self.wStr[word])
            temp += "\n"
            f.write(temp)
        f.close()
        self.curDocID += 1
        self.wCount.clear()
        self.wStr.clear()

class MergeFiles():
    def __init__(self, outputdir, statfile, iter):
        self.outputdir = outputdir
        self.statfile = statfile
        self.iter = iter
        self.words = 0

    def mergeIndex(self):
        self.files = glob.glob(self.outputdir+'/*-'+str(self.iter)+'.txt')
        t = self.merge("-"+str(self.iter), 0)

    def extractWord(self, line, start): #start - new word or not
        if ":" in line:
            if start:
                word =  line.split(':',1)[0].rsplit('|',1)[-1].strip()
                postlist = line.split(':',1)[1].strip()
                return word, postlist, False #still the same word in the line
            else:
                word = ""
                postlist = line.split(':',1)[0].rsplit('|',1)[0]
                return word, postlist, True #new word in the line
        else :
            word = ""
            postlist += line.strip()
            return word, postlist, False
        
    def getWordPostlist(self, f): #returns word, postlist, remianing bool or not
        if f.closed:
            print("should not be here at all")
            return "","", False
        fpos = f.tell()
        line = f.readline()
        if(line == ""):
            return "", "", False
        word, postlist, t = self.extractWord(line, True)
        while(1):
            fpos = f.tell()
            line = f.readline()
            if(line == ""):
                f.seek(fpos)
                return word, postlist, True
            w, p, end = self.extractWord(line, False)
            word += w
            postlist += p
            if end:
                f.seek(fpos)
                return word, postlist, True    

    def merge(self, endName, finalstatus): 
        print("inside merge index\n")
        # -1 that will be the endName or nothing
        self.words = 0
        fList = [None] * len(self.files)
        localWStr = [None] * len(self.files)
        endStatus = [None] * len(self.files)
        fflag = True #ending of merging when all files have stopped reading
        cnt = 0

        if finalstatus == 1:
            indexfile = self.outputdir+"/INDEX.txt"
            fIndex = open(indexfile, "a+")

        for i in range(len(self.files)):
            f = open(self.files[i], "r")
            f.seek(0,0)
            fList[i]=f
            # print("inital asking for "+str(self.files[i]))
            w, p, end = self.getWordPostlist(f)
            localWStr[i] = [w,p]
            if end == False:
                # print("intial file to be closed is "+str(self.files[i]))
                f.close()
            else :
                cnt += 1
            endStatus[i] = end
        
        if fflag == False or cnt<=0:
            fflag = False

        # print("fflag\n")
        # print(fflag)
        # print("files to be tackled\n")
        # for i in range(len(self.files)):
        #     print(self.files[i]+" "+str(endStatus[i]))

        while fflag:
            indexFCnt = 0 #number of index- txt files
            outputfile = self.outputdir+"/index-"+str(indexFCnt)+str(endName)+".txt"
            fOutput = open(outputfile, "w+")
            # print("current index/output file "+str(outputfile)+"\n")
            self.numLines = 0
            startword, startpostlist = "", ""
            endword, endpostlist = "", ""
            
            tempNum = 0
            while(self.numLines < 100000000):
                minword, minpostlist = "", ""
                mini = -1
                cnt = 0
                for i in range(len(self.files)):
                    if fList[i].closed:
                        endStatus[i] = False
                    if endStatus[i] == True:
                        cnt +=1 
                        if minword == "":
                            [minword, minpostlist] = localWStr[i]
                            mini = i

                        else :
                            if localWStr[i][0] < minword:
                                [minword, minpostlist] = localWStr[i]

                if fflag == False or cnt<=0:
                    fflag = False
                    break
                
                if mini>-1 and endStatus[mini]:
                    w, p, end = self.getWordPostlist(fList[mini])
                    localWStr[mini] = [w,p]
                    if end == False:
                        # print("file to be closed "+str(self.files[mini]))
                        f.close()
                    endStatus[mini] = end

                if startword == "":
                    startword = minword
                    startpostlist = minpostlist
                    endword = minword
                    endpostlist = minpostlist
                else :
                    if endword < minword:
                        temp = str(endword)+":"+str(endpostlist)+"\n"
                        self.numLines += 1
                        self.words += 1
                        fOutput.write(temp)
                        self.numLines += 1
                        self.words += 1
                        endword = minword
                        endpostlist = minpostlist
                    elif endword == minword:
                        endpostlist += minpostlist
                    else:
                        print("\n\nERROR SHOULD NOT HAPPEN IN MERGE\n\n")

            if endword != "":
                temp = str(endword)+":"+str(endpostlist)+"\n"
                self.numLines+=1
                # print("new word\n")
                self.words+=1
                fOutput.write(temp)            
            fOutput.close()
            self.numLines = 0
            indexFCnt += 1

            if finalstatus == 1:
                temp = "" + startword+":"+endword+"|"+outputfile+"\n"
                fIndex.write(temp)
            
        if finalstatus == 1:
            fIndex.close()

        # for fle in self.files:
        #     open(fle, 'w').close()
        #     os.remove(fle)

        return self.words

    def externalMerge(self):
        self.files = glob.glob(self.outputdir+'/index-*.txt')
        words = self.merge("", 1)
        return words

class WikiHandler(sax.ContentHandler):       
    def __init__(self, outputdir, statfile, iter):
        self.docID = 0
        self.outputdir = outputdir
        self.statfile = statfile
        self.iter = iter
        self.textproc = TextProcessor(self.outputdir, self.statfile, self.iter)
        self.titletxt = open(self.outputdir+"/"+str(self.iter)+"-title.txt", "w+")
        self.initialize()

    def initialize(self):
        self.currenttag = ""
        self.title = ""
        self.infobox = ""
        self.inum = 0
        self.references = ""
        self.rnum = 0
        self.externallink = ""
        self.enum = 0
        self.categories = ""
        self.body = ""

    def startElement(self, tag, attrs):
        self.currenttag = tag

    def endElement(self, tag):
        if tag == "page":
            self.titletxt.write(self.title.lower())
            self.textproc.processText(self.title, "title", self.docID)
            self.textproc.processText(self.infobox, "infobox", self.docID)
            self.textproc.processText(self.references, "references", self.docID)
            self.textproc.processText(self.externallink, "externallink", self.docID)
            self.textproc.processText(self.categories, "categories", self.docID)
            self.textproc.processText(self.body, "body", self.docID)

            self.textproc.createIndex()
            self.initialize()
            self.docID += 1
     

    def endDocument(self):
      self.textproc.writeIndex()
      self.titletxt.close()
    #   self.textproc.createStat()
    #   print("stat file created\n")
      
    def characters(self, content):
        if self.rnum > 0:
            self.inum = 0
            self.enum  = 0
            if content != "" and len(content) > 0 and len(re.sub(r"\s+", "", content)) > 0 and content[0:2] == "{{":
                temp = content.strip() + " ;"
                self.references += temp
            elif content != "" and len(content) > 0 and len(re.sub(r"\s+", "", content)) > 0:
                self.rnum = 0   
      
        if self.enum >0:
            self.rnum = 0
            self.inum  = 0
            if content != "" and len(content) > 0 and len(re.sub(r"\s+", "", content)) > 0 and ( content[0] == '*' or content[0:2] == "{{") :
                temp = content.strip() + " ;"
                self.externallink += temp
            elif content != "" and len(content) > 0 and len(re.sub(r"\s+", "", content)) > 0:
                self.enum = 0  

        if self.currenttag == "title":
            self.title += content
        elif self.currenttag == "text":
            if "{{Infobox" in content:
                self.inum += 1
                temp = content.find("{{Infobox")
                content = content[temp+9:]
            elif "== References ==" in content:
                self.rnum = 1
            elif "== External links ==" in content:
                self.enum = 1
            elif "[[Category" in content:
                try:
                    p = re.compile("\[\[Category:(.*)\]\]")
                    result = p.search(content)
                    temp = result.group(1) +" ;"
                    self.categories += temp
                except:
                    pass
            else:
                self.body += content

        if self.inum > 0:
            self.rnum = 0
            self.enum  = 0
            if "}}" in content:
                self.inum -= content.count('}}')
            if "{{" in content:
                self.inum += content.count('{{')

            if self.inum <= 0:
                temp = content.rfind('}}')
                self.infobox += content[:temp]
            else :
                self.infobox += content     

if __name__ == "__main__":
    print("arguments to python")
    print(sys.argv)

    if sys.argv[5] == '1':
        mergeproc = MergeFiles(sys.argv[2], sys.argv[3], sys.argv[4])
        words = mergeproc.externalMerge()
        statproc = CreateStatFile(sys.argv[2], sys.argv[3],words)
        exit(1)

    start_time = time.time()

    reader = sax.make_parser([])
    handler = WikiHandler(sys.argv[2], sys.argv[3], sys.argv[4])
    reader.setContentHandler(handler)
    reader.parse(open(sys.argv[1]))
    smerge_time = time.time()
    mergeproc = MergeFiles(sys.argv[2], sys.argv[3], sys.argv[4])
    mergeproc.mergeIndex()

    print("files merged and document end: time taken "+str(time.time()-smerge_time)+"\n")
    print("title num at the end "+str(handler.docID)+"\n")

    time_taken = time.time() - start_time
    print("time taken for" + str(sys.argv[4])+" : "+str(time_taken)+"\n")
    
    # open(sys.argv[1], 'w').close()
    # os.remove(sys.argv[1])
    
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
from nltk.tokenize import word_tokenize
# import nltk.stem as stemmer
import Stemmer
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.stem.snowball import SnowballStemmer
import time
class TextProcessor():
    def __init__(self, outputdir):
        self.createOutputDir(outputdir)
        # porter = PorterStemmer()
        # lancaster=LancasterStemmer()
        # self.stemer = Stemmer.Stemmer('english')
        self.englishStemmer=SnowballStemmer("english")
        self.wCount = {}
        self.max = 200 #combine these many file's index lists
        self.wStr = {}
        self.curDocID = 0
        self.docID = 0
        self.count = 0

    def removePunctiotion(self, text):
        res = re.sub(r'[^\w\s]', ' ', text)
        return res

    def tokenize(self, text):
        word_tokens = word_tokenize(text)
        return word_tokens 

    def removeStopwords(self, tokens):
        filtered_tokens = []
        stop_words = set(stopwords.words('english')) 
        for token in tokens: 
            if token not in stop_words: 
                filtered_tokens.append(token)
        return filtered_tokens

    def stem(self, text):
        storeStem = {}
        stemmedWord = []
        for word in text:
            if word not in storeStem:
                storeStem[word] = self.englishStemmer.stem(word)
                # storeStem[word] = self.stemer.stemWord(word)
            stemmedWord.append(storeStem[word])
        
        storeStem.clear()
        return stemmedWord

    def processText(self, text, tag, docId):
        self.docID =docId
        textP = self.removePunctiotion(text)
        textP = textP.lower()
        textFinal = self.stem(self.removeStopwords(self.tokenize(textP)))
        for word in textFinal:
          if word.strip() == '':
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

    def createOutputDir(self, outputdir):
        try:
            os.mkdir(outputdir) 
        except FileExistsError:
            pass

    def createIndex(self, outputdir):
        for word in self.wCount:
            temp = ""
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
            self.writeIndex(outputdir)

    def writeIndex(self, outputdir):
        f = open(str(outputdir) + "/"+ str(self.curDocID)+".txt","w+")
        for word in self.wStr:
            temp = str(word)
            temp += ":"
            temp += str(self.wStr[word])
            temp += "\n"
            f.write(temp)
        f.close()
        self.curDocID += 1
        self.wCount.clear()
        self.wStr.clear()

    def createStat(self, statfile):
        f = open(statfile,"w+")
        f.write(str(self.count)+"\n")
        f.close()

class MergeFiles():
    def __init__(self, outputdir, outputfile, statfile):
        self.files = glob.glob(str(outputdir)+'/*.txt')
        # print(self.files)
        # print("===============================")
        self.wStr = {}
        while(len(self.files)>2):
            temp = []
            for i in range(0, len(self.files), 2):
                if i >= (len(self.files)-1):
                    temp.append(self.files[i])
                else:
                    temp.append(self.merge(self.files[i], self.files[i+1], False))
            self.files = temp
        if len(self.files) == 2:
          self.files = [self.merge(self.files[0], self.files[1], True)]
          
        # f = open(self.files[0],"r+")
        # content = f.readlines()
        # f.close()
        # f = open(outputfile, "w+")
        # f.write(content)
        # f.close()
        # del content

        # open(self.files[0], 'w').close()
        # os.remove(self.files[0])
        self.addStat(self.files[0], statfile)

    def addStat(self, outputfile, statfile):
        f = open(outputfile, "r+")
        content = f.readlines()
        cnt = 0

        for line in content:
            if ":" in line:
                cnt += 1
        
        f = open(statfile,"a+")
        f.write(str(cnt))
        f.close()

    def createDic(self, content):
        word = ""
        postlist = ""
        for line in content:
          if ":" in line:
              if word not in self.wStr:
                  self.wStr[word] = str(postlist)
              else :
                  self.wStr[word] += str(postlist)
              [word, postlist] = line.split(":",1)
              postlist = postlist.strip()       
          else :
            postlist += line.strip()  
        if word not in self.wStr:
            self.wStr[word] = str(postlist)
        else :
            self.wStr[word] += str(postlist)         

    def merge(self, file1, file2, flag):
        f1 = open(file1, "r")
        f2 = open(file2, "r")
        self.wStr = {}
        self.createDic(f1.readlines())
        self.createDic(f2.readlines())
        f1.close()
        f2.close()
        
        f = open(file1, "w+")
        if flag:
          for word in sorted(self.wStr):
              temp = str(word)
              temp += ":"
              temp += str(self.wStr[word])
              temp += "\n"
              f.write(temp)
        else :
           for word in self.wStr:
              temp = str(word)
              temp += ":"
              temp += str(self.wStr[word])
              temp += "\n"
              f.write(temp)         
        f.close()
        open(file2, 'w').close()
        os.remove(file2)
        return file1

class WikiHandler(sax.ContentHandler):       
    def __init__(self, outputdir, outputfile, statfile):
        self.textproc = TextProcessor(outputdir)
        self.docID = 0
        self.outputdir = outputdir
        self.outputfile = outputfile
        self.statfile = statfile
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
            self.textproc.processText(self.title, "title", self.docID)
            self.textproc.processText(self.infobox, "infobox", self.docID)
            self.textproc.processText(self.references, "references", self.docID)
            self.textproc.processText(self.externallink, "externallink", self.docID)
            self.textproc.processText(self.categories, "categories", self.docID)
            self.textproc.processText(self.body, "body", self.docID)

            self.textproc.createIndex(self.outputdir)
            self.initialize()
            self.docID += 1

            if self.docID>10000 :
                pass
            # print("doc ID "+str(self.docID)+" ")       

    def endDocument(self):
      self.textproc.writeIndex(self.outputdir)
      self.textproc.createStat(self.statfile)
      print("stat file created\n")
      mergeproc = MergeFiles(self.outputdir, self.outputfile, self.statfile)
      print("files merged and document end\n")
      
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
    # start_time = time.time()
    # reader = sax.make_parser([])
    # outputdir = os.path.abspath(os.getcwd()) + "/indexes"
    # handler = WikiHandler(outputdir, sys.argv[2], sys.argv[3])

    # reader.setContentHandler(handler)
    # reader.parse(open(sys.argv[1]))

    # time_taken = time.time() - start_time
    # print("time taken for indexing: "+str(time_taken)+"\n")

    start_time = time.time()
    reader = sax.make_parser([])
    handler = WikiHandler("./indexes","./indexfile.txt", "./statfile.txt")

    reader.setContentHandler(handler)
    reader.parse(open("../enwiki-20200801-pages-articles-multistream1.xml-p1p30303"))
    time_taken = time.time() - start_time
    print("time taken: "+str(time_taken)+"\n")
import glob
import time
import sys

class Search():
    def __init__(self, outputfile):
        self.file = outputfile

    def searchByWord(self, searchText):
        f = open(self.file, 'r')
        searchWords = searchText.lower().split(" ")
        for searchWord in searchWords:
            while 1:
                line = f.readline()
                if not line: 
                    break
                [word, postlist] = line.split(":",1)
                postlist = postlist.strip()
                if word == searchWord:
                    print("============= RESULT: " + str(searchWord)+ "===================")
                    print(postlist)
                    print("=========================================")

    def searchByPostList(self, searchPostList):
        if "t:" in searchPostList:
            temp = searchPostList.split("t:")[1].split(" ")[0]
            self.searchByWord(temp)
        if "i:" in searchPostList:
            temp = searchPostList.split("i:")[1].split(" ")[0]
            self.searchByWord(temp)
        if "c:" in searchPostList:
            temp = searchPostList.split("c:")[1].split(" ")[0]
            self.searchByWord(temp)
        if "b:" in searchPostList:
            temp = searchPostList.split("b:")[1].split(" ")[0]
            self.searchByWord(temp)
        if "r:" in searchPostList:
            temp = searchPostList.split("r:")[1].split(" ")[0]
            self.searchByWord(temp)
        if "l:" in searchPostList:
            temp = searchPostList.split("l:")[1].split(" ")[0]
            self.searchByWord(temp)  

if __name__ == "__main__":
    start_time = time.time()
    searcher  = Search(sys.argv[1])
    query = str(sys.argv[2]).strip()

    if ":" in query:
        searcher.searchByPostList(query)
    else :
        searcher.searchByWord(query)

    time_taken = time.time() - start_time
    print("time taken for searching: "+str(time_taken)+"\n")
# *SEARCH ENGINE*
This is a small scale implementation of a *Search Engine* written in Python and Bash and using libraries such as xml.sax and resource. Topics such as **Parsing**, **Tokenization**, **Stemming**, **Lemmetization** and **Memory management** are used. This reduces the data size to 1/3rd roughly and does searching in less than a minute.

## *Usage*
For indexing
```
bash index.sh <path_to_outputdir> <path_to_statfile>
```
For searching
```
bash search.sh <path_to_index_files> <path_to_query_file> <path_to_queryop_file>
```


## *Explanation*

### *Indexing*
The XML zips are downloaded and unzipped and each xml file is parsed seperately and far later merged. First we parse the XML file, getting the title, infobox, links, references, body and categories for each page of each xml file. This is done using XML.sax handler. Then for around 500 of those pages we create a ```<num>-<iter>.txt ``` is created, where ```<iter>``` is the ```<iter>```th number of xml file processed. This merge is done using maps/dictionaries.

Each line of the doc is of form :
```
word:n<num>d<num>t<num>i<num>r<num>e<num>c<num>b<num>|...
```

the n represents the nth xml file processed

the d represents the docID of the page and corresponding
title present inside the xml file

the t represents the frequency of the word in a title

the i represents the frequency of the word in a infobox

the r represents the frequency of the word in a reference

the e represents the frequency of the word in a link

the c represents the frequency pf the word in a category

the b represents the frequency of the word in a body

The text processing is combined of basic splits, strips, PyStemmer, tokenization and removal of stopwords, punctuations and non-english symbols. I have also meddled with Snowball stemmer and Portal stemmer for accuracy and speed.

Final merging for the xml file is done in a merge-k fashion to combine ```<num>-<iter>.txt``` to ```index-<num>-<iter>.txt``` files. In the end, after processing all the index files, we create the ```index-<num>.txt``` files, using external merge. While doing so, we create the ```INDEX.txt``` file.


### *Searching*
Using the ```<iter>-title.txt```, ```index-<num>.txt``` files and ```INDEX.txt``` files, we search the queries.

First we process the files and get the processed words and the corresponding tags to search for. Then for each word, we search the ```INDEX.txt``` file to get the corresponding index file name and get the postlists. Processing the postlists will provide us the title num (the title txt number to search for) and docID (the docID to search for the specific title txt file).
The common pair of the previously mentioned results will give the titles. Using the scoring method depending on the corresponding tags and our own weights,
we do a dot product with the occurences in each field to give us a score. Based on the descending order, we get the most relevant k files.

All results are written into a query op file

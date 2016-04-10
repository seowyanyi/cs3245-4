This is the README file for A0086626W's submission

Email: a0086626@u.nus.edu
== General Notes about this assignment ==

Place your comments or requests here for Min to read.  Discuss your
architecture or experiments in general.  A paragraph or two is usually
sufficient.

The general strategy is to use a enhanced version of tf-idf. 

Enhancements: 
 - Query expansion. Take top 10% of documents and use their most frequent words to execute another query  (commented out due to poor performance), 
- Adding similar terms. hypernyms, synonyms of nouns and verbs.
- Filtering of invalid characters like punctuation and numbers. I only whitelisted alphabets and '-', rationale being only words and not numbers are descriptive of what a patent is about. This reduces the noise in the data. 
- Removal of patent-specific stopwords, on top of nltk stopwords
- Usage of a three-stage approach. 


1. Indexing Stage
The postings list data structure has term frequency as part of a tuple, not just document id. 
I have also added meta data about the corpus - document length and number of documents.
Document length is computed by first converting the raw token count to 1 + log(tf)
Both pieces of meta data are used later in the Searching Stage for lnc.ltc computation.

There are also additional patent meta data like UPC, IPC, family members, cited_by.


2. High precision searching stage
This is a high-precision low-recall search. We do a high-precision search by not adding any additional terms. This is used to get a proxy for true postive so we can increase precision when doing addition searches later on, by comparing results to this set.

Tokens are split into description_tokens and title_tokens. Higher weightage is given to the "title" field of query in tf-idf because it is usually more concise and informative. 

When a unique term in the document being examined appears in the "title" field of query, we increment a frequency counter. Later on, we check which documents have a high occurence of terms in the query title and multiply  (1 + math.log(high_priority_freq, 10)) to it. 


3. High recall searching stage
The third stage performs a higher recall search with the addition of query expansion (disabled in final code) and adding of hypernyms, synonyms. The precision is improved by boosting document scores if their patent fields (family, cited_by, IPC, UPC) are similar to the proxy true postive.

Finally, I return the top 95% of results. 

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

search.py - the querying logic.
index.py - indexer entry point
indexer.py - main logic of indexer
inverted_index.py - data structure for my inverted index
helper.py - helper functions for the various files.
teamname.txt - my teamname

meta_data.txt - pickled meta data of document lengths, number of docs, UPC, IPC, family members, cited_by, top 10 occurring terms in a document (for use in query expansion)
dictionary.txt - pickled dictionary
postings.txt - pickled postings file
ESSAY.txt - answers to essay questions



== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0086626W, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[] I, A0086626W, did not follow the class rules regarding homework
assignment, because of the following reason:

I suggest that I should be graded as follows:


== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
This is the README file for A0086626W's submission

Email: a0086626@u.nus.edu
== General Notes about this assignment ==

Place your comments or requests here for Min to read.  Discuss your
architecture or experiments in general.  A paragraph or two is usually
sufficient.

1. Indexing Stage
The postings list data structure is extended to support term frequency as part of a tuple, not just document id. 
I have also added meta data about the corpus - document length and number of documents.
Document length is computed by first converting the raw token count to 1 + log(tf)
Both pieces of meta data are used later in the Searching Stage for lnc.ltc computation.

2. Searching Stage
At the start, meta data and dictionary is fetched from disk. 
Given a particular query, I first calculate the query ltc for all query terms.
We then loop through the query terms, fetch postings list and to calculate document lnc and the corresponding product for each document. This product is saved into the Scores class.

At the end, we call the get_top_results method of the Scores class. This method sorts the scores by their magnitude as well as doc ids in the event of a draw. The top 10 results are then returned.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

search.py - the querying logic.
index.py - indexer entry point
indexer.py - main logic of indexer
inverted_index.py - data structure for my inverted index

meta_data.txt - pickled meta data
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
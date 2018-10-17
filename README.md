# BioOntology
uakron.edu/BRIC/E2BMO 

Here is an attempt to explain the steps one can take to generate the results we have created: 

1- Getting Trade-Offs from BMO MASTER file

Open the GetResults.py in a text editor 

Change /Library/WebServer/Documents/E2BMO/CGI-Executables/   with appropriate address of your folder on your computer

Make sure BMO MASTER  is in the filename at the beginning of GetResults.py

Open terminal in your computer, 

write  cd [location of your python code] 

then write : python GetResults.py 'speed-accuracy trade-off' Noun

This creates a file named : speed-accuracy trade-off_trade_offs.txt   -> rename it to speed-accuracy_trade_offs.txt

Repeat this for all the Trade-offs



2- Getting E2BMO

This step needs to be performed after getting all the txt files from step 2.

Open the GetResults.py in a text editor , change BMO MASTER  with  BMOSKOS_V3 file

In console write  python GetResults.py ‘branch’ Function 

This creates 2 files  ‘branch_BiologicalText.txt’ and ‘branch_graph.csv’

Repeat this step for all the E2B words



3- Putting it all together - The website 

Create a folder data/

Put all the files from step 1 and 2 into this folder 

Put data/ folder in E2BMO/ folder

Put E2BMO/ folder on your server

Just use the link to E2BMO on your web browser to access the files.



Important notes:
Note: am using JavaScript to access the files. This and  google graphics for E2BMO need a server connection.

Note: to run python codes, one need to change folder addresses with appropriate ones. 

Note : One needs python 3 coding language installed on their computer 

Note: BMOMASTER and BMOSKOS_V3 are both XML_RDF format files exported from BMO in Protoge 

Note: BMOSKOS_V3 is the SKOS added words to BMO

content on this site is licensed under a Creative Commons Attribution 4.0 International license. 

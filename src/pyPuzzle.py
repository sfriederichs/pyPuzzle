#!/usr/bin/python
""""
NPR Puzzle Script 1/31/21
Version 0.1 Build 1 (1/31/21)
Author: Stephen Friederichs
License: Beerware License: If you find this program useful and you ever met me, buy me a beer. (I like Saisons)
This script will hopefully provide the answer to the NPR Puzzle
posed on 1/31/21, which is as follows:
If you start driving in Montana, you can drive to South Dakota, and from
there to Iowa. If you take the postal abbreviations (MT,IA,SD) and 
rearrange the letters you can make the word 'amidst'.
If you drive through four states, you can make another word in a similar
way. What states, and what word?

A reduced set of correct answers is:

{'AL->GA->TN->VA': {'galavant'}, 
 'AR->TN->MO->NE': {'ornament'}, 
 'AR->TN->MO->IA': {'animator'}, 
 'AR->TN->GA->FL': {'flagrant'}, 
 'AR->MO->NE->SD': {'ransomed'}, 
 'AR->MO->IL->MO': {'mailroom'}, 
 'AR->MO->IA->SD': {'dioramas'}, 
 'CO->NE->SD->NE': {'condense'}, 
 'CO->NE->SD->MN': {'condemns'}, 
 'IL->MO->NE->KS': {'moleskin'}, 
 'IL->MO->AR->LA': {'amarillo'}, 
 'IA->NE->MO->TN': {'nominate'}, 
 'MO->IA->SD->ND': {'diamonds'}, 
 'SD->NE->CO->UT': {'contused'},
 
The following command-line parameters control the behavior of the script:
-h, --help - Shows this screen and exits
-v, --version - Display version information
-l, --license - Display author and license information
-f, --logfilepath=<PATH> - Set the log file path
-e, --loglevel=<LEVEL> - Set log level: DEBUG, INFO, WARNING, ERROR
"""

import textwrap
import logging
import getopt
import sys
import datetime
import re
import itertools
from threading import Thread
from spellchecker import SpellChecker

#Derived from here: https://thefactfile.org/u-s-states-and-their-border-states/
stateBorderData = """
1.	Alabama	Mississippi, Tennessee, Florida, Georgia	4
2.	Alaska	None	None
3.	Arizona	Nevada, New Mexico, Utah, California, Colorado	5
4.	Arkansas	Oklahoma, Tennessee, Texas, Louisiana, Mississippi, Missouri	6
5.	California	Oregon, Arizona, Nevada 3
6.	Colorado	New Mexico, Oklahoma, Utah, Wyoming, Arizona, Kansas, Nebraska	7
7.	Connecticut	New York, Rhode Island, Massachusetts	3
8.	Delaware	New Jersey, Pennsylvania, Maryland	3
9.	Florida	Georgia, Alabama	2
10.	Georgia	North Carolina, South Carolina, Tennessee, Alabama, Florida	5
11.	Hawaii	None	None
12.	Idaho	Utah, Washington, Wyoming, Montana, Nevada, Oregon	6
13.	Illinois	Kentucky, Missouri, Wisconsin, Indiana, Iowa, Michigan	6
14.	Indiana	Michigan, Ohio, Illinois, Kentucky	4
15.	Iowa	Nebraska, South Dakota, Wisconsin, Illinois, Minnesota, Missouri	6
16.	Kansas	Nebraska, Oklahoma, Colorado, Missouri	4
17.	Kentucky	Tennessee, Virginia, West Virginia, Illinois, Indiana, Missouri, Ohio	7
18.	Louisiana	Texas, Arkansas, Mississippi	3
19.	Maine	New Hampshire	1
20.	Maryland	Virginia, West Virginia, Delaware, Pennsylvania	4
21.	Massachusetts	New York, Rhode Island, Vermont, Connecticut, New Hampshire	5
22.	Michigan	Ohio, Wisconsin, Illinois, Indiana, Minnesota (water border)	5
23.	Minnesota	North Dakota, South Dakota, Wisconsin, Iowa, Michigan (water border)	5
24.	Mississippi	Louisiana, Tennessee, Alabama, Arkansas	4
25.	Missouri	Nebraska, Oklahoma, Tennessee, Arkansas, Illinois, Iowa, Kansas, Kentucky	8
26.	Montana	South Dakota, Wyoming, Idaho, North Dakota	4
27.	Nebraska	Missouri, South Dakota, Wyoming, Colorado, Iowa, Kansas,	6
28.	Nevada	Idaho, Oregon, Utah, Arizona, California	5
29.	New Hampshire	Vermont, Maine, Massachusetts	3
30.	New Jersey	Pennsylvania, Delaware, New York	3
31.	New Mexico	Oklahoma, Texas, Utah, Arizona, Colorado	5
32.	New York	Pennsylvania, Rhode Island (water border), Vermont, Connecticut, Massachusetts, New Jersey	6
33.	North Carolina	Tennessee, Virginia, Georgia, South Carolina	4
34.	North Dakota	South Dakota, Minnesota, Montana	3
35.	Ohio	Michigan, Pennsylvania, West Virginia, Indiana, Kentucky	5
36.	Oklahoma	Missouri, New Mexico, Texas, Arkansas, Colorado, Kansas	6
37.	Oregon	Nevada, Washington, California, Idaho	4
38.	Pennsylvania	New York, Ohio, West Virginia, Delaware, Maryland, New Jersey	6
39.	Rhode Island	Massachusetts, New York (water border), Connecticut	3
40.	South Carolina	North Carolina, Georgia,	2
41.	South Dakota	Nebraska, North Dakota, Wyoming, Iowa, Minnesota, Montana	6
42.	Tennessee	Mississippi, Missouri, North Carolina, Virginia, Alabama, Arkansas, Georgia, Kentucky	8
43.	Texas	New Mexico, Oklahoma, Arkansas, Louisiana	4
44.	Utah	Nevada, New Mexico, Wyoming, Arizona, Colorado, Idaho	6
45.	Vermont	New Hampshire, New York, Massachusetts	3
46.	Virginia	North Carolina, Tennessee, West Virginia, Kentucky, Maryland	5
47.	Washington	Oregon, Idaho	2
48.	West Virginia	Pennsylvania, Virginia, Kentucky, Maryland, Ohio	5
49.	Wisconsin	Michigan, Minnesota, Illinois, Iowa	4
50.	Wyoming	Nebraska, South Dakota, Utah, Colorado, Idaho, Montana	6"""


#Copied directly from here: https://gist.github.com/rogerallen/1583593
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

""" 
This function is designed to be started as a thread. It adds the words it can find in the permutations
of the path string to the validWords dictionary.

Args:
* path - The string representing the path through the states visisted
* validWords - The dictionary of valid words - keys are the path strings, values are valid words derived from that path
* d - The SpellChecker object that tells us if we have valid words
"""

def workerThread(path,validWords,d):
    knownWords = d.known([''.join(p) for p in itertools.permutations(path)])
    if len(knownWords) >0:
        validWords[path] = knownWords
"""
This is the function that generates the list of strings that represent the path through *depth+1* states
It uses recursion to generate the list

Args:
* startingStatePc - The postal code abbreviation of the state we're starting in
* stateBorderDict - Dictionary of states and their bordering states
* string - The path string that has been generated so far
* depth - The number of states remaining to visit in the path

"""

def generatePathString(startingStatePc,stateBorderDict,string="",depth=3):
    retPathList = []
    
    #We're going to use this twice, so assign it to a variable once
    borderStatesList = stateBorderDict[startingStatePc]
    
    #Add the current state to the path string
    string += startingStatePc

    if depth > 1:  #If we're not at the endpoint of our journey, call this function again for all bordering states
        for borderState in borderStatesList:
            retPathList.extend(generatePathString(borderState,stateBorderDict,string,depth-1))
    else:           #We ARE at the endpoint of our journey, so start generating a list of strings
        retPathList = [string+statePcAbbrev for statePcAbbrev in borderStatesList]
    
    return retPathList
        
    
""" 
This function parses the big bad multiline string above which contains the list of states and the other states
that border them. It uses regular expressions to do so.

Args:
* string - The multiline string containing the state/border data
* pcList - Dictionary of state names and their postal code abbreviatons
"""
def parseStateBorderString(string= stateBorderData,pcList=us_state_abbrev):
    stateBorderDict = {}
    
    for line in stateBorderData.splitlines():
        logging.debug("Line is %s",line)
        matches = re.findall("[0-9]+.[\s]+([A-Za-z ]+)[\t]+([A-Za-z,\(\) ]+)",line)       
        
        if len(matches) >0:
            logging.debug("Found matches: %s",str(matches))
            (state,borderListStr) = matches[0]
            logging.debug("State is %s, borderList is %s",state,borderListStr)
            
            state = state.strip()
            borderStateList = [x.strip() for x in borderListStr.split(',')]
            logging.debug("Border state list is %s",str(borderStateList))
            

            try:
                statePostalCode = pcList[state]
            except KeyError:
                print("State " + str(state) + " has no postal code abbreviation in the list")
                return {}
            logging.debug("State '"+str(state) + "' has abbreviation '"+str(statePostalCode) +"'")

            borderStatePcList = []
            for borderState in borderStateList:
                try:
                    pcAbbrev = pcList[borderState]
                    logging.debug("Abbreviation for '%s' is '%s'",borderState,pcAbbrev)
                except KeyError:
                    logging.debug("Found invalid state in border list: %s",borderState)
                    continue
                borderStatePcList.append(pcAbbrev)
            stateBorderDict[statePostalCode]=borderStatePcList
                        
    return stateBorderDict
    
"""This function properly formats docstrings for printing on the console"""
def prettyPrint(uglyString):
    #Remove all newlines
    uglyString = uglyString.replace('\n','').replace('\r','')
    #Use textwrap module to automatically wrap lines at 79 characters of text
    print(textwrap.fill(uglyString,width=79))
    
""" Command-line reporting functions """
def license():
    for line in __doc__.splitlines()[2:4]:
        prettyPrint(line)
        
def help():
    for line in __doc__.splitlines()[4:]:
        prettyPrint(line)

def version():
    prettyPrint(__doc__.splitlines()[2])
 
def progId():
    prettyPrint(__doc__.splitlines()[1])

"""Main function"""

def main():
    progId()
    
    logFilePath = datetime.datetime.now().strftime('logs/log_%H_%M_%d_%m_%Y.log')

    #Configure logging
    logLevel = logging.DEBUG 
    formatStr = '%(asctime)s - %(threadName)s - %(funcName)s  - %(levelname)-8s %(message)s'
    
    try: 
        opts, args = getopt.getopt(sys.argv[1:], 'hvlf:e:', ['help','version','license','logfile=','loglevel='])    
    except getopt.GetoptError:
        print("Bad argument(s)")
        help()
        sys.exit(2) 
        
    #Evaluate command-line arguments
    for opt, arg in opts:                 
        if opt in ('-h', '--help'):     
            help()                         
            sys.exit(0)                 
        elif opt in ('-l','--license'):    
            license()
        elif opt in ('-f','--logfilepath'):
            logFilePath=str(arg)
        elif opt in ('-e','--loglevel='):
            try:
                if str(arg).upper() == "DEBUG":
                    logLevel=logging.DEBUG
                elif str(arg).upper() == "INFO":
                    logLevel= logging.INFO
                elif str(arg).upper() == "WARNING":
                    logLevel= logging.WARNING
                elif str(arg).upper() == "ERROR":
                    logLevel = logging.ERROR
                else:
                    raise ValueError
            except ValueError:
                print("Bad logging level")
                help()
                sys.exit(2)
        elif opt in ('-v','--version'):
            version()
            sys.exit(0)
        else:
            print("Bad command line argument: "+str(opt)+" - " +str(arg))
            help()
            sys.exit(2)
    #Initialize logging to a file
    logging.basicConfig(filename=logFilePath,filemode='a',level=logLevel,format=formatStr)
    
    #Then, retrieve a StreamHandler - this outputs log data to the console
    console = logging.StreamHandler()

    #Now configure the stream handler to the same settings as the file handler
    #Note, however that you don't need them both to be configured the same - it may be
    #entirely appropriate to have different settings for console vs. file.

    formatter = logging.Formatter(formatStr)
    console.setLevel(logLevel)
    console.setFormatter(formatter)

    #And finally, attach the console handler to the logger so the output goes both places
    logging.getLogger('').addHandler(console)

    logging.debug("Logging is configured - Log Level %s , Log File: %s",str(logLevel),logFilePath) 
    
    #Application code
    
    #Get the state/border information from the bigstring
    stateBorderDict = parseStateBorderString()
    
    #Use threads to evaluate all of the 4-state paths to determine if there are any words that can be
    #made from the letters in the postal code abbreviations for the states visisted
    
    #List for thread handles
    threadHandles = []
    
    #Dictionary for valid words - keys are the path strings, values are a list of valid words formed from the letters in the
    #key
    validWords = {}    
    
    #Used to provide some feedback on how far along we are
    threadsStarted = 0
    
    spell = SpellChecker()
    
    #Get the list of state postal code abbreviations
    statePcAbbrevs = stateBorderDict.keys()
    
    for state in statePcAbbrevs:
        #Generate path strings going through 4 states starting with *state*
        for path in generatePathString(state,stateBorderDict):
            #Start a new thread to handle each path produced for this starting state
            threadHandles.append(Thread(target=workerThread,args=(path,validWords,spell,))  )
            threadHandles[-1].start()  
            
            #Provide some feedback on how much progress we've made
            threadsStarted += 1
            if threadsStarted % 25 == 0:
                print("Started " +str(threadsStarted) + " threads")
                
    print("Started all threads!")
    
    #Join all started threads to close everything out
    threadsComplete = 0
    for handle in threadHandles:
        handle.join()
        threadsComplete +=1
        if threadsComplete %25 == 0:
            print("Closed " +str(threadsComplete) + " threads out of "+str(len(threadHandles)))
            
    #Print out the list of valid words derived from each path string
    for pathString,words in validWords.items():
        print(str("->".join([pathString[n:n+2] for n in range(0,8,2)]) + " - "  + ",".join(words)))
        
            

    
    


if __name__ == "__main__":
    # execute only if run as a script
    main()
'''
   Copyright (c) 2018 Jack Farley
   This file is part of Twatter
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
  Twatter.py
   ------------
'''
from __future__ import unicode_literals
from __future__ import print_function
import os
import sys
import logging
import argparse
from biplist import *
import sqlite3
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
import twitter
import json
import re
import pathlib2 as pathlib

TWATTER_STR = """
  _______            _   _            
 |__   __|          | | | |           
    | |_      ____ _| |_| |_ ___ _ __ 
    | \ \ /\ / / _` | __| __/ _ \ '__|
    | |\ V  V / (_| | |_| ||  __/ |   
    |_| \_/\_/ \__,_|\__|\__\___|_|   
"""

def open_db(inputPath):
    try:
        conn = sqlite3.connect(inputPath)
        return conn
    except:
        print("Failed to open ", inputPath)
    return None


# Extremely simple function to check if path exists
def validate_archive_path(archivePath):
    if os.path.exists(archivePath):
        if os.path.isdir(archivePath):
            return 1
        else:
            return 0
    else:
        return 0

#def validate_output_path(ouputPath):

# Returns path of Twitter archive directory to work with
def get_argument():
    print(TWATTER_STR)
    parser = argparse.ArgumentParser(description='Utility to parse out Twitter Archive')

    #  Gets path to Twitter Archive
    parser.add_argument('-a', '--archive', required=True, type=str, nargs='+', dest='archivePath', help='Path to Twitter Archive Folder')
    parser.add_argument('-o', '--output', required=True, type=str, nargs='+', dest='outputPath', help='Filepath to output database')

    argumentsPaths = []

    args = parser.parse_args()
    if args.outputPath[0]:

        # Checks if database already exists
        ouputPathEdit = pathlib.Path(args.outputPath[0])
        exists = ouputPathEdit.is_file()
        if exists:
            print("ERROR: Database already exists or Not a Valid Directory\n")
            exit()
        else:

            # Checks to see if the output file is a creatable file in an accessible folder
            creatable = os.access(os.path.dirname(args.outputPath[0]), os.W_OK)
            if creatable:
                argumentsPaths.append(args.outputPath[0])
            else:
                print("ERROR: Not a valid path")
                exit(0)

    else:
        print("ERROR: No output path given")

    if args.archivePath[0]:
        archivePathEdit = pathlib.Path(args.archivePath[0])
        exists = archivePathEdit.is_dir()
        if exists:
            if args.archivePath[0].endswith("\\"):
                argumentsPaths.append(args.archivePath[0])
                return argumentsPaths
            else:
                fixedPath = str(args.archivePath[0]) + "\\"
                return argumentsPaths.append(fixedPath)
        else:
            print("ERROR: Not a valid directory \n")
            exit()
    
# Function that returns array of values from javascript files
def getDict(filepath):
    dataArr = []
    file = open(filepath, "r")
    parser = Parser()
    tree = parser.parse(file.read())
    fields = {getattr(node.left, 'value', ''): getattr(node.right, 'value', '')
          for node in nodevisitor.visit(tree)
          if isinstance(node, ast.Assign)}

    # Edit the values obtained from the .js and append them to their own array
    for keys, values in fields.iteritems():
        newValues = values.strip("\"")
        dataArr.append(str(newValues))
    
    # Pop off two empty elements in array
    dataArr.pop(0)
    dataArr.pop(0)

    file.close()
    return dataArr
        
# Function to parse account information from account.js
def account(path):

    # Opens databse and initializes path names
    # TODO - ADD FILE CHECKING
    db = open_db(path[0])
    accountPath = path[1] + "\\account.js"
    ipPath = path[1] + "\\account-creation-ip.js"

    # Fills arrays with data from files
    accountData = getDict(accountPath)
    ipData = getDict(ipPath)

    fieldQuery = "CREATE TABLE Account_Info(Username, Display_Name, Email, PhoneNum, AccountID, CreatedIP, CreatedAt, Timezone, CreatedVia)"

    # Executes the create table, then inserts the data
    db.execute(fieldQuery)
    db.execute("INSERT INTO Account_Info (Username, Display_Name, Email, PhoneNum, AccountID, CreatedIP, CreatedAt, Timezone, CreatedVia) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (accountData[3], accountData[2], accountData[5], accountData[6], accountData[1],ipData[0], accountData[4], accountData[7], accountData[0]))

    db.commit()

def getDataFromTweet(regEx, inputStr):
    data = re.search(regEx, inputStr)
    if data:
        data = data.group(0)
        return data
    else:
        return "NULL"


def tweets(path):
    # Opens databse and initializes path names
    # TODO - ADD FILE CHECKING
    db = open_db(path[0])
    tweetPath = path[1] + "\\tweet.js"

    retweetArr = []
    sourceArr = []
    favCountArr = []
    tweetIdArr = []
    tweetTextArr = []
    createdAtArr = []
    mediaUrlArr = []

    # All regex expressions
    retweetedRX = "(.*),"
    sourceRX = "(?<=source\" : )(.*)(?=,)"
    favoriteCountRx = "(?<=favorite_count\" : \")(.*)(?=\",)"
    tweetIdRx = "(?<=\"id\" : \")(.*)(?=\",)"
    tweetTextRx = "(?<=\"full_text\" : \")(.*)(?=\",)"
    createdAtRx = "(?<=\"created_at\" : \")(.*)(?=\",)"
    mediaUrlRx = "(?<=\"media_url_https\" : \")(.*)(?=\")"

    singleTweets = open(tweetPath).read().decode("utf-8").split("\"retweeted\" : ")
    for i, twts in enumerate(singleTweets):
        singleTweets[i] = twts.encode("utf-8")
    singleTweets.pop(0)
    for i in range(0, len(singleTweets)):

        # Gets Retweet bool
        retweetArr.append(getDataFromTweet(retweetedRX, singleTweets[i].decode("utf-8")))

        # Gets Source
        sourceArr.append(getDataFromTweet(sourceRX, singleTweets[i].decode("utf-8")))

        # Gets favorite count
        # FIX SO IT RECOGNIZES AS INT
        favCountArr.append(getDataFromTweet(favoriteCountRx, singleTweets[i].decode("utf-8")))

        # Gets Tweet ID
        tweetIdArr.append(getDataFromTweet(tweetIdRx, singleTweets[i].decode("utf-8")))

        # Gets Tweet Text
        # FIX SO IT RECOGNIZES AS INT
        tweetTextArr.append(getDataFromTweet(tweetTextRx, singleTweets[i].decode("utf-8")))

        # Gets Created At Date/Time
        createdAtArr.append(getDataFromTweet(createdAtRx, singleTweets[i].decode("utf-8")))

        # Gets media URLS in HTTPS format
        mediaUrlArr.append(getDataFromTweet(mediaUrlRx, singleTweets[i].decode("utf-8")))

        i+=1
    
    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Tweets(Tweet_Text, TweetID, CreatedAt, FavCount, Source, Retweeted, MediaURL)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(tweetTextArr)):
        db.execute("INSERT INTO Tweets (Tweet_Text, TweetID, CreatedAt, FavCount, Source, Retweeted, MediaURL) values (?, ?, ?, ?, ?, ?, ?)", 
                    (tweetTextArr[j], tweetIdArr[j], createdAtArr[j], favCountArr[j], sourceArr[j], retweetArr[j], mediaUrlArr[j]))

    db.commit()
    db.close()

def main():
    archivePath = []
    archivePath = get_argument()
    account(archivePath)
    tweets(archivePath)


if __name__ == "__main__":
    main()

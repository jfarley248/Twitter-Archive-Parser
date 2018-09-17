'''
   Copyright (c) 2018 Jack Farley
   This file is part of Twitter-Archive-Parser
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
  Twitter-Archive-Parser.py
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
import re
import pathlib2 as pathlib
import requests
import time
import datetime

# Initialize dictionary to better performance
# And yes, that is my Twitter
KNOWN_USERS = {'1718780184':['Jack Farley', '@JackFarley248']}


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


# Returns path of Twitter archive directory to work with
def get_argument():
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
            sys.exit()
        else:

            # Checks to see if the output file is a creatable file in an accessible folder
            creatable = os.access(os.path.dirname(args.outputPath[0]), os.W_OK)
            if creatable:
                argumentsPaths.append(args.outputPath[0])
            else:
                print("ERROR: Not a valid path")
                sys.exit()

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
            sys.exit()
    
# Gets Name & handle 
def idToData(userId):

    # Checks global variable to see if data has already been entered. 
    # Huge performance increase plus only one https request per unknown user
    if userId in KNOWN_USERS:
        return KNOWN_USERS.get(userId)

    else:
        # Initializes array for full name and Twitter handle
        data = []

        # Reg ex for getting full name and Twitter handle
        fullNameRx = "(?<=<title>)(.*)(?= \()"
        handleRx = "(?<=<p><span class=\"nickname\">)(.*)(?=<\/span><\/p>)"


        # Gets data from Twitter site
        # Need to wait to not overrequest and lose data
        time.sleep(.6)
        url = "https://twitter.com/intent/user?user_id=" + userId
        request = requests.get(url)


        fullName = getDataFromTweet(fullNameRx, request.text)
        handle = getDataFromTweet(handleRx, request.text)

        if fullName:
            data.append(fullName)
        else:
            data.append("ERROR")
        if handle:
            data.append(handle)
        else:
            data.append("ERROR")

        # Adds new user data to dictionary
        KNOWN_USERS.update({userId:[data[0], data[1]]})

        return data
    

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
    db = open_db(path[0])
    accountPath = path[1] + "\\account.js"
    ipPath = path[1] + "\\account-creation-ip.js"

    # Fills arrays with data from files
    accountData = getDict(accountPath)
    ipData = getDict(ipPath)

    fieldQuery = "CREATE TABLE Account_Info(Username TEXT, Display_Name TEXT, Email TEXT, PhoneNum INTEGER, AccountID INTEGER, CreatedIP BLOB, CreatedAt DATE, Timezone TEXT, CreatedVia TEXT)"

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
    fieldQuery = "CREATE TABLE Tweets(Tweet_Text TEXT, TweetID INT, CreatedAt DATE, FavCount INT, Source TEXT, Retweeted BOOLEAN, MediaURL TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(tweetTextArr)):
        db.execute("INSERT INTO Tweets (Tweet_Text, TweetID, CreatedAt, FavCount, Source, Retweeted, MediaURL) values (?, ?, ?, ?, ?, ?, ?)", 
                    (tweetTextArr[j], tweetIdArr[j], createdAtArr[j], favCountArr[j], sourceArr[j], retweetArr[j], mediaUrlArr[j]))

    db.commit()
    db.close()

# Function to parse Login IP address info
def ipLogins(path):
    db = open_db(path[0])
    ipPath = path[1] + "\\ip-audit.js"
    ipInfo = open(ipPath, "r")

    # Inintializes arrays to store variables
    accountIdArr = []
    createdAtArr = []
    loginIpArr = []

    # Reg Ex variables
    accountIdRx = "(?<=accountId\" : \")(.*)(?=\",)"
    createdAtRx = "(?<=createdAt\" : \")(.*)(?=\",)"
    loginIpRx = "(?<=loginIp\" : \")(.*)(?=\")"


    # Fills accountIdArr
    for lines in ipInfo:
        accountId = re.search(accountIdRx, lines)
        if accountId != None:
            accountIdArr.append(accountId.group(0))

        # Fills createdAtArr
        createdDate = re.search(createdAtRx, lines)
        if createdDate != None:
            createdAtArr.append(createdDate.group(0))

        # Fills loginIpArr
        loginIp = re.search(loginIpRx, lines)
        if loginIp != None:
            loginIpArr.append(loginIp.group(0))

    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Logins_From_IP(AccountID INTEGER, Username TEXT, Handle TEXT, IP_Addr BLOB, CreatedAt DATE)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(accountIdArr)):
        user = idToData(accountIdArr[j])
        db.execute("INSERT INTO Logins_From_IP (AccountID, Username, Handle, IP_Addr, CreatedAt) values (?, ?, ?, ?, ?)", 
                    (accountIdArr[j], user[0], user[1], loginIpArr[j], createdAtArr[j]))

    
    db.commit()
    db.close()
    ipInfo.close()

# Gets blocked users from block.js
# Will run into problems with HTTPs requests after a hundred requests give or take. 
def blocked(path):
    db = open_db(path[0])
    blockPath = path[1] + "\\block.js"
    blockInfo = open(blockPath, "r")

    # Inintializes arrays to store variables
    blockedIdArr = []

    # Reg Ex variables
    blockedIdRx = "(?<=\"accountId\" : \")(.*)(?=\")"

    # Fills blockedIdArr
    for lines in blockInfo:
        blockedId = re.search(blockedIdRx, lines)
        if blockedId != None:
            blockedIdArr.append(blockedId.group(0))

    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Blocked_Users(AccountID INTEGER, Username TEXT, Handle TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(blockedIdArr)):
        user = idToData(blockedIdArr[j])
        db.execute("INSERT INTO Blocked_Users (AccountID, Username, Handle) values (?, ?, ?)", 
                    (blockedIdArr[j], user[0], user[1]))
    
    db.commit()
    db.close()
    blockInfo.close()

# Parses out direct messages from direct-message.js
def slideIntoThoseDms(path):
    db = open_db(path[0])
    dmPath = path[1] + "\\direct-message.js"


    dms = open(dmPath).read().decode("utf-8").split("\"messageCreate\" : ")
    for i, singleDm in enumerate(dms):
        dms[i] = singleDm.encode("utf-8")
    dms.pop(0)


    # Inintializes arrays to store variables
    recipIdArr = []
    senderIdArr = []
    textArr = []
    mediaUrlArr = []
    messageIdArr = []
    createdAtArr = []

    # Reg Ex variables
    recipIdRx = "(?<=\"recipientId\" : \")(.*)(?=\",)"
    senderIdRx = "(?<=\"senderId\" : \")(.*)(?=\",)"
    textRx = "(?<=\"text\" : \")(.*)(?=\",)"
    mediaUrlRx = "(?<=\"mediaUrls\" : )(.*)(?=,)"
    messageIdRx = "(?<=\"id\" : \")(.*)(?=\",)"
    createdAtRx = "(?<=\"createdAt\" : \")(.*)(?=\")"


    for i in range(0, len(dms)):

        # Gets Recipient bool
        recipIdArr.append(getDataFromTweet(recipIdRx, dms[i].decode("utf-8")))

        # Gets Sender
        senderIdArr.append(getDataFromTweet(senderIdRx, dms[i].decode("utf-8")))

        # Gets text
        textArr.append(getDataFromTweet(textRx, dms[i].decode("utf-8")))

        # Gets media URL
        mediaUrlArr.append(getDataFromTweet(mediaUrlRx, dms[i].decode("utf-8")))

        # Gets message ID
        messageIdArr.append(getDataFromTweet(messageIdRx, dms[i].decode("utf-8")))

        # Gets Created At Date/Time
        createdAtArr.append(getDataFromTweet(createdAtRx, dms[i].decode("utf-8")))

        i+=1
    
    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Direct_Messages(Message_ID INTEGER, Sender_Name TEXT, Recipient_Name TEXT, Message TEXT, Created_At DATE, SenderID INTEGER, RecipientID INTEGER, SenderHandle TEXT, RecipientHandle TEXT, Media_URL TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(messageIdArr)):
        sender = idToData(senderIdArr[j])
        recipient = idToData(recipIdArr[j])
        db.execute("INSERT INTO Direct_Messages (Message_ID, Sender_Name, Recipient_Name, Message, Created_At, SenderID, RecipientID, SenderHandle, RecipientHandle, Media_URL) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (messageIdArr[j], sender[0], recipient[0], textArr[j], createdAtArr[j], senderIdArr[j], recipIdArr[j], sender[1], recipient[1], mediaUrlArr[j]))

    db.commit()
    db.close()

# Correlates data about a users contacts
def contacts(path):
    db = open_db(path[0])
    contactPath = path[1] + "\\contact.js"


    contact = open(contactPath).read().decode("utf-8").split("\"contact\" : ")
    for i, singleContact in enumerate(contact):
        contact[i] = singleContact.encode("utf-8")
    contact.pop(0)
 

    # Inintializes arrays to store variables
    contactIdArr = []
    emailArr = []
    phoneNumArr = []


    # Reg Ex variables
    contactIdRx = "(?<=\"id\" : \")(.*)(?=\")"
    emailRx = "(?<=\"emails\" : )(.*)(?=,)"
    phoneNumRx = "(?<=\"phoneNumbers\" : \[ \")(.*)(?=\")"

    for i in range(0, len(contact)):

        # Gets Contact ID
        contactIdArr.append(getDataFromTweet(contactIdRx, contact[i].decode("utf-8")))

        # Gets Email
        emailArr.append(getDataFromTweet(emailRx, contact[i].decode("utf-8")))

        # Gets Phone Number
        phoneNumArr.append(getDataFromTweet(phoneNumRx, contact[i].decode("utf-8")))

        i+=1
    
    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Imported_Contacts(Contact_ID INTEGER, Phone_Number TEXT, Email TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(contactIdArr)):
        db.execute("INSERT INTO Imported_Contacts (Contact_ID, Phone_Number, Email) values (?, ?, ?)", 
                    (contactIdArr[j], phoneNumArr[j], emailArr[j]))

    db.commit()
    db.close()

def following(path):
    db = open_db(path[0])
    followingPath = path[1] + "\\following.js"


    following = open(followingPath).read().decode("utf-8").split("\"following\" : ")
    for i, singlefollowing in enumerate(following):
        following[i] = singlefollowing.encode("utf-8")
    following.pop(0)

    # Inintializes arrays to store variables
    accountIdArr = []

    # Reg Ex variables
    accountIdRx = "(?<=accountId\" : \")(.*)(?=\")"

    for i in range(0, len(following)):

        # Gets Account ID
        accountIdArr.append(getDataFromTweet(accountIdRx, following[i].decode("utf-8")))

        i+=1

    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Following(Account_ID INTEGER, Username TEXT, Handle TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(accountIdArr)):
        user = idToData(accountIdArr[j])
        db.execute("INSERT INTO Following (Account_ID, Username, Handle) values (?, ?, ?)", 
                    (accountIdArr[j], user[0], user[1]))

    db.commit()
    db.close()

# Gets users followers from followers.js
def followers(path):
    db = open_db(path[0])
    followingPath = path[1] + "\\follower.js"


    followers = open(followingPath).read().decode("utf-8").split("\"follower\" : ")
    for i, singlefollowers in enumerate(followers):
        followers[i] = singlefollowers.encode("utf-8")
    followers.pop(0)

    # Inintializes arrays to store variables
    accountIdArr = []

    # Reg Ex variables
    accountIdRx = "(?<=accountId\" : \")(.*)(?=\")"

    for i in range(0, len(followers)):

        # Gets Account ID
        accountIdArr.append(getDataFromTweet(accountIdRx, followers[i].decode("utf-8")))

        i+=1

    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Followers(Account_ID INTEGER, Username TEXT, Handle TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(accountIdArr)):
        user = idToData(accountIdArr[j])
        db.execute("INSERT INTO Followers (Account_ID, Username, Handle) values (?, ?, ?)", 
                    (accountIdArr[j], user[0], user[1]))

    db.commit()
    db.close()

# Gets connected applications from connected-applications.js
def connectedApps(path):
    db = open_db(path[0])
    connectPath = path[1] + "\\connected-application.js"


    connects = open(connectPath).read().decode("utf-8").split("\"connectedApplication\" : ")
    for i, singleConnects in enumerate(connects):
        connects[i] = singleConnects.encode("utf-8")
    connects.pop(0)
   

    # Inintializes arrays to store variables
    orgNameArr = []
    orgUrlArr = []
    nameArr = []
    msecApproveArr = []
    permArr = []
    descArr = []

    # Reg Ex variables
    orgNameRx = "(?<=      \"name\" : \")(.*)(?=\")"
    orgUrlRx = "(?<=\"url\" : )(.*)(?=)"
    nameRx = "(?<=\"name\" : \")(.*)(?=\",\s    \")"
    msecApproveRx = "(?<=\"approvedAtMsec\" : \")(.*)(?=\")"
    permRx = "(?<=\"permissions\" : )(.*)(?=,)"
    descRx = "(?<=\"description\" : \")(.*)(?=\")"


    for i in range(0, len(connects)):

        # Gets Organization Name
        orgNameArr.append(getDataFromTweet(orgNameRx, connects[i].decode("utf-8")))

        # Gets Organization URL
        orgUrlArr.append(getDataFromTweet(orgUrlRx, connects[i].decode("utf-8")))

        # Gets Name of App
        nameArr.append(getDataFromTweet(nameRx, connects[i].decode("utf-8")))

        # Gets millisecond approved time
        msecApproveArr.append(getDataFromTweet(msecApproveRx, connects[i].decode("utf-8")))

        # Gets App Permissions
        permArr.append(getDataFromTweet(permRx, connects[i].decode("utf-8")))

        # Gets Description of App
        descArr.append(getDataFromTweet(descRx, connects[i].decode("utf-8")))

        i+=1
 

    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Connected_Apps(App_Name TEXT, Organization_Name TEXT, Description TEXT, Approved_Date DATE, Permissions TEXT, Organization_URL TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0,len(orgNameArr)):
        db.execute("INSERT INTO Connected_Apps (App_Name, Organization_Name, Description, Approved_Date, Permissions, Organization_URL) values (?, ?, ?, ?, ?, ?)", 
                    (nameArr[j], orgNameArr[j], descArr[j], datetime.datetime.fromtimestamp(float(msecApproveArr[j])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'), permArr[j], orgUrlArr[j]))

    db.commit()
    db.close()



def main():

    #Initializes and fills array with path to Archive and path to output db
    archivePath = []
    archivePath = get_argument()

    # Times process
    start = time.time()


    # Calls all pasing functions
    contacts(archivePath)
    contactTime = time.time()
    print("\nImported Contacts Processed in ", contactTime - start, " Seconds\n")

    account(archivePath)
    accountTime = time.time()
    print("Account Info Processed in ", accountTime - contactTime, " Seconds\n")

    slideIntoThoseDms(archivePath)
    dmTime = time.time()
    print("Direct Messages Processed in ", dmTime - accountTime, " Seconds\n")

    tweets(archivePath)
    tweetTime = time.time()
    print("Tweets Processed in ", tweetTime - dmTime, " Seconds\n")

    followers(archivePath)
    followerTime = time.time()
    print("Followers Processed in ", followerTime - tweetTime, " Seconds\n")

    ipLogins(archivePath)
    ipLoginTime = time.time()
    print("IP Logins Processed in ", ipLoginTime - followerTime, " Seconds\n")

    blocked(archivePath)
    blockTime = time.time()
    print("Blocked Users Processed in ", blockTime - ipLoginTime, " Seconds\n")

    connectedApps(archivePath)
    connTime = time.time()
    print("Connected Apps Processed in ", connTime - blockTime, " Seconds\n")

    following(archivePath)
    followTime = time.time()
    print("Followed Users Processed in ", followTime - blockTime, " Seconds\n")

    end = time.time()
    print("Processing Complete \n Total Time: ", end - start, " Seconds\n")

if __name__ == "__main__":
    main()

import re
import sqlite3
import requests
import time

KNOWN_USERS = {'1718780184':['Jack Farley', '@JackFarley248']}
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

def open_db(inputPath):
    try:
        conn = sqlite3.connect(inputPath)
        return conn
    except:
        print("Failed to open ", inputPath)
    return None

def getDataFromTweet(regEx, inputStr):
    data = re.search(regEx, inputStr)
    if data:
        data = data.group(0)
        return data
    else:
        return "NULL"


def main():
    dmPath = 'ENTER FULL PATH TO direct-message.js'
    db = open_db("Twitter_Archive_Parser_Output.db")

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

        i += 1

    # Initializes & adds data to database
    fieldQuery = "CREATE TABLE Direct_Messages(Message_ID INTEGER, Sender_Name TEXT, Recipient_Name TEXT, Message TEXT, Created_At DATE, SenderID INTEGER, RecipientID INTEGER, SenderHandle TEXT, RecipientHandle TEXT, Media_URL TEXT)"
    db.execute(fieldQuery)
    j = 0
    for j in range(0, len(messageIdArr)):
        sender = idToData(senderIdArr[j])
        recipient = idToData(recipIdArr[j])
        db.execute(
            "INSERT INTO Direct_Messages (Message_ID, Sender_Name, Recipient_Name, Message, Created_At, SenderID, RecipientID, SenderHandle, RecipientHandle, Media_URL) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
            messageIdArr[j], sender[0], recipient[0], textArr[j], createdAtArr[j], senderIdArr[j], recipIdArr[j], sender[1],
            recipient[1], mediaUrlArr[j]))

    db.commit()
    db.close()

if __name__ == '__main__':
    main()

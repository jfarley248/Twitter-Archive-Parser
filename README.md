# Twatter
Python Script to parse Twitter Archive


## Prerequisites
* Windows Environment
* Python 2
* Following Packages Installed Via Pip
  * `pip install lxml`
  * `pip install requests`
  * `pip install slimit`
* OR use bundled executable

## Running the Script
```
usage: Twatter.py [-h] [-a ARCHIVEPATH [ARCHIVEPATH ...]]

Utility to parse out Twitter Archive

optional arguments:
  -h, --help            show this help message and exit
  -a ARCHIVEPATH [ARCHIVEPATH ...], --archive ARCHIVEPATH [ARCHIVEPATH ...]
                        Path to Twitter Archive
```

EXAMPLE: `python .\Twatter.py -a C:\Users\jfarley248\Desktop\Twitter_Folder`

## Current Functionality
* Ouputs data to SQLite DB
* Parses Basic Account info from account.js
* Parses Tweet Data from tweet.js

## Current Issues
* Needs a lot more testing
* Fix output database being overwritteen, tell user DB already exists (easy fix)
* Needs better file verifications

## Future Implementations
* Logging
* Get Twitter username from ID without using Twitter API
* More data files to parse
  * Blocked Users
  * Liked Tweets
  * Contacts
  * Connected Apps
  * Basically every other .js file
 

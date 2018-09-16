# Twatter
```
  _______            _   _
 |__   __|          | | | |
    | |_      ____ _| |_| |_ ___ _ __
    | \ \ /\ / / _` | __| __/ _ \ '__|
    | |\ V  V / (_| | |_| ||  __/ |
    |_| \_/\_/ \__,_|\__|\__\___|_|
```

Python Script to parse Twitter Archives

*Current Version: 0.01b* 

## Prerequisites
* Windows Environment
* Python 2
* Following Packages Installed Via Pip
  * `pip install lxml`
  * `pip install requests`
  * `pip install slimit`
  * `pip install pathlib2`
  * `pip install BeautifulSoup`
* OR use bundled executable

## Running the Script
```

usage: Twatter.py [-h] -a ARCHIVEPATH [ARCHIVEPATH ...] -o OUTPUTPATH
                  [OUTPUTPATH ...]

Utility to parse out Twitter Archive

optional arguments:
  -h, --help            show this help message and exit
  -a ARCHIVEPATH [ARCHIVEPATH ...], --archive ARCHIVEPATH [ARCHIVEPATH ...]
                        Path to Twitter Archive Folder
  -o OUTPUTPATH [OUTPUTPATH ...], --output OUTPUTPATH [OUTPUTPATH ...]
                        Filepath to output database
```

EXAMPLE: `python .\Twatter.py -a C:\Users\jfarley248\Desktop\Twitter\ -o C:\Users\jfarley248\Desktop\ouput.db`

## Current Functionality
* Ouputs data to SQLite DB
* Parses Basic Account info from account.js
* Parses Tweet Data from tweet.js

## Currently Known Issues
* Needs a lot more testing

## Future Implementations
* Logging
* Get Twitter username from ID without using Twitter API
* More data files to parse
  * Blocked Users
  * Liked Tweets
  * Contacts
  * Connected Apps
  * Basically every other .js file
 

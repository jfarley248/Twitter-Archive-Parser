# Twitter-Archive-Parser


Python Script to parse Twitter Archives

*Current Version: 1.0* 

## Prerequisites
* Windows Environment
* Python 2
* Following Packages Installed Via Pip
  * `pip install lxml`
  * `pip install requests`
  * `pip install slimit`
  * `pip install pathlib2`
* OR use bundled executable

## Running the Script
```

usage: Twitter-Archive-Parserr.py [-h] -a ARCHIVEPATH [ARCHIVEPATH ...] -o OUTPUTPATH
                  [OUTPUTPATH ...]

Utility to parse out Twitter Archive

optional arguments:
  -h, --help            show this help message and exit
  -a ARCHIVEPATH [ARCHIVEPATH ...], --archive ARCHIVEPATH [ARCHIVEPATH ...]
                        Path to Twitter Archive Folder
  -o OUTPUTPATH [OUTPUTPATH ...], --output OUTPUTPATH [OUTPUTPATH ...]
                        Filepath to output database
```

EXAMPLE: `python .\Twitter-Archive-Parser.py -a C:\Users\jfarley248\Desktop\Twitter\ -o C:\Users\jfarley248\Desktop\ouput.db`

## Current Functionality
* Ouputs data to SQLite DB
* Parses Data From
  * account.js
  * tweet.js
  * ip-audit.js
  * block.js
  * direct-message.js
  * contact.js
  * follower.js
  * following.js
  * connected-application.js

## Currently Known Issues
* Needs a lot more testing

## Future Implementations
* Logging
* Find optimal sub-routine calling process
* Ad Data Parsing
 

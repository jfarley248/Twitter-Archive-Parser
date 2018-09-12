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



DATABASE = "output.db"


def open_db(inputPath):
    try:
        conn = sqlite3.connect(inputPath)
        return conn
    except:
        print("Failed to open ", inputPath)
    return None


# Extremely simple function to check if path exists
def validate_path(archivePath):
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
    parser.add_argument('-a', '--archive', type=str, nargs='+', dest='archivePath', help='Path to Twitter Archive (.zip)')

    args = parser.parse_args()
    if args.archivePath[0]:
        exists = validate_path(args.archivePath[0])
        if exists:
            if args.archivePath[0].endswith("\\"):
                return args.archivePath[0]
            else:
                str(args.archivePath[0]) + "\\"
                return args.archivePath[0]
        else:
            print("Not a valid directory \n")
            sys.exit()
        
# Function to parse account information from account.js
def account(path):

    data = []

    # Query to create table for data
    query = """

        CREATE TABLE IF NOT EXISTS Account_Info (
            Username text,
            Display_Name text,
            Email text,
			Phone_Num text,
            Account_ID int,
			Created_At,
			Created_Via text,
			Timezone text
                                    );

    """
    # Execute Query
    db = open_db(DATABASE)
    db.execute(query)

    path = path + "\\account.js"
    file = open(path, "r")
    parser = Parser()
    tree = parser.parse(file.read())
    fields = {getattr(node.left, 'value', ''): getattr(node.right, 'value', '')
          for node in nodevisitor.visit(tree)
          if isinstance(node, ast.Assign)}
    for keys, values in fields.iteritems():
        newKeys = keys.strip("\"")
        newValues = values.strip("\"")
        
        fields[newKeys] =fields.pop(keys)
        fields[newKeys] = newValues

    for keys, values in fields.iteritems():
        if values:
            data.append(values)
        else:
            continue
    
    for items in data:
        db.execute('insert into Account_Info items (?,?,?)', items)   
    
    file.close()


def main():
    archivePath = get_argument()

    # Creates database for output
    conn = sqlite3.connect(r"output.db")
    account(archivePath)



if __name__ == "__main__":
    main()

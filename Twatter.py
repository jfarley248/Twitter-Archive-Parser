'''
   Copyright (c) 2018 Jack Farley
   This file is part of Twatter
   Usage or distribution of this software/code is subject to the
   terms of the GNU GENERAL PUBLIC LICENSE.
  Twatter.py
   ------------
'''
from __future__ import print_function
from __future__ import unicode_literals
import logging
import os
import sys
import argparse

#log = logging.getLogger('Got_MElk.')  # Logger object
#logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

def get_argument():
    parser = argparse.ArgumentParser(description='Utility to parse out Twitter Archive')

    #  Gets path to Memory File
    parser.add_argument('-a', '--archive', type=str, action='store_const', const=archivePath, nargs='+',
                        help='Path to Twitter Archive')

    #  Gets OS Profile, runs imageinfo and selects appropriate profile if not specified
    parser.add_argument('-p','--profile', type=str, nargs='+',
                        help='''Memory Profile to use, if not specified, imageinfo will run and detect the most
                                appropriate profile, case sensitive''')

    #  Gets path to config file
    parser.add_argument('-c', metavar='--config', type=str, nargs='+',
                        help='Path to config file, if not specified, default file will be used')

    args = parser.parse_args()
    imagePath = args.i[0]
    profile = args.p[0]
    configPath = args.c[0]
    return(imagePath, profile, configPath)

# -*- coding: utf-8 -*-

'''
    Descrição do programa!
'''

import codecs
import time
import os
import zipfile
import tarfile
import urllib2
import subprocess
import maxminddb as geo
import socket
import io

jack=os.listdir("/Users/pedro/CTI/ID/MLab/NDT/Results/2014/03/01/")
print jack

def cleanlist(input):
    ok=0
    while ok==0:
        ok=1
        for x in range(len(input)):
            y = input[x].split(".")
            if y[-1]!="txt":
                del input[x]
                ok=0
                break
    return input

johez =["aaa.txt",
        "bbb.txt",
        "a.c",
        "johen.del",
        "jorge.txt",
        "adeline.txt",
        "Hat.hat",
        "jo.txt"
        ]

cleanlist(johez)
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

#!/usr/bin/python

import StringIO
import shutil
import tempfile
#from gslib.third_party.oauth2_plugin import oauth2_plugin

import boto

# URI scheme for Google Cloud Storage.
GOOGLE_STORAGE = 'gs'
# URI scheme for accessing local files.
LOCAL_FILE = 'file'

url="gs://m-lab/ndt/2014/01/01/20140101T000000Z-mlab4-nuq01-ndt-0000.tgz"

'''
#subprocess.call('gsutil cp gs://m-lab/ndt/2014/02/01/20140201T000000Z-mlab4-nuq01-ndt-0001.tgz "/Volumes/External Data/"', shell=True)
noia='gs://m-lab/ndt/2014/02/01/'
testao=subprocess.check_output('gsutil ls '+noia, shell=True)

for x in testao:
    print x

teste=testao.split("\n")

print teste

'''
def downloader(data,destino,primeiro,ultimo):
    ultimo+=1
    primeiro-=1
    gspath = 'gs://m-lab/ndt/' + data + '/'
    tarlist = subprocess.check_output('gsutil ls ' + gspath, shell=True)
    tarlist = tarlist.split('\n')
    for index in range(primeiro,ultimo):
        chamada = 'gsutil cp ' + tarlist[index] + " " + destino
        subprocess.call(chamada, shell=True)
    locallist=[]
    for index in range(primeiro,ultimo):
        fpath = tarlist[index]
        fname = fpath.split("/")
        fname = str(fname[-1])
        locallist.append(destino + fname)
    return locallist

jeack = downloader('2014/02/01','/Users/pedro/Downloads/',1,5)

print jeack


'''
    basepath="/Users/pedro/CTI/ID/MLab/NDT/"
    tar=basepath+"20140201T000000Z-mlab1-ams01-ndt-0000.tgz"
    
    filelist=texpand(tar,1)
    mfilelist=metalist(filelist)
    print mfilelist
    print len(mfilelist)
    
    input=basepath+mfilelist[0]
    int=reader(input)
    final={}
    for x in int:
    final[x]=[]
    
    for x in mfilelist:
    input=basepath+x
    int=reader(input)
    for y in int:
    final[y].append(int[y])
    
    #os.rmdir(basepath+"2012/01/05/")
    #os.rmdir(basepath+"2012/01/")
    #os.rmdir(basepath+"2012/")
    
    print "Final length is " + str(len(final))
    i=1
    for x in final:
    print "Then we go on to " + str(i) + " " + str(len(final[x]))
    print "By the way, this is " + x
    i+=1
    
    print final["web100_33"]
    print len(final["web100_33"])
    createout(tar+".csv",final)
    
    for x in filelist:
    x=basepath+x
    os.remove(x)
    '''
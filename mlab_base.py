# -*- coding: utf-8 -*-

'''
Descrição do programa!
'''

import codecs
import time
import os
import zipfile
import tarfile
import csv

'''

dictionarye = [
"Date/Time",
"c2s_snaplog file",
"c2s_ndttrace file",
"s2c_snaplog file",
"s2c_ndttrace file",
"cputime file",
"server IP address",
"server hostname",
"server kernel version",
"client IP address",
"client hostname",
"client OS name",
"client_browser name",
"client_application name",
"Summary data",
" * Additional data",
]

minidic = [
"Date/Time",
"server IP address",
"client IP address",
"client hostname",
"client OS name",
"client_browser name",
"client_application name",
"Summary data",
]

'''



def parser(input):
    inpath=""
    temppath=input.split("/")
    for x in range(len(temppath)-1):
        inpath+=str(temppath[x])+"/"
    
    tempname=temppath[-1].split(".")
    inname=tempname[-2]
    return inpath,inname

def reader(input):
    output={}
    file = open(input,"r")

    for x in file:
        x = x.split(":")
        header=x[0]
        results=""
        for i in range(1,len(x)):
            if i>1: results=results+":"
            results=results+x[i]
        results = results.replace("\n","")
        results = results.replace(" ","")
        output[header]=results

    web100 = output["Summary data"].split(",")
    i=2
    for x in web100:
        header="web100_"+str(i)
        output[header]=x
        i+=1
    output.pop("Summary data")
    return output

def texpand(input,extraction=0):
    ttotal=time.time()
    tfil=time.time()
    print "Extracting filenames..."
    targuy=tarfile.open(input,"r")
    namelist=targuy.getnames()
    tfil=time.time()-tfil
    print "Extracted filenames in: ",tfil," seconds."
    if extraction!=0:
        text=time.time()
        print "Extracting files..."
        inpath,inname=parser(input)
        for f in targuy:
            try:
                targuy.extract(f,inpath)
            except IOError as e:
                os.remove(inpath+f.name)
                targuy.extract(f,inpath)
        text=time.time()-text
        print "Extracted files in: ",text," seconds."
    return namelist

def metalist(input):
    output=[]
    for x in input:
        jon = x.split(".")
        if jon[-1]=="meta": output.append(x)
    return output

def createout(path,outname,input):
    outfile=file(path+outname,"w")
    listed=[]
    i=0
    sortee=sorted(input)
    for key in sortee:
        listed.append([])
        listed[i].append(key)
        for x in input[key]:
            listed[i].append(x)
        i+=1
        transposed=[]
        for k in range(len(listed[0])):
            row=[]
            for j in range(len(listed)):
                row.append(listed[j][k])
            transposed.append(row)
    writer=csv.writer(outfile)
    writer.writerows(transposed)




basepath="/Users/pedro/CTI/ID/MLab/"
tar=basepath+"20120105T000000Z-mlab1-ams01-ndt-0000.tgz"

filelist=texpand(tar,1)
mfilelist=metalist(filelist)

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

for x in filelist:
    x=basepath+x
    os.remove(x)
#os.rmdir(basepath+"2012/01/05/")
#os.rmdir(basepath+"2012/01/")
#os.rmdir(basepath+"2012/")

createout(basepath,"teste.csv",final)
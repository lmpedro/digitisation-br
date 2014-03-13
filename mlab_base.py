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
import subprocess

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
        if header==" * Additional data": break
        results=""
        for i in range(1,len(x)):
            if i>1: results=results+":"
            results=results+x[i]
        results = results.replace("\n","")
        results = results.replace(" ","")
        output[header]=results

    web100 = output["Summary data"].split(",")
    if len(web100)!=53:
        return 0
    else:
        i=3
        for x in web100:
            header="web100_%02i" %i
            output[header]=x
            i+=1
        output.pop("Summary data")
        return output

def texpand(input,extraction=1):
    ttotal=time.time()
    tfil=time.time()
    print "\nExtracting filenames..."
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

def createout(output,input):
    print "\nCreating summary file..."
    outfile = open(output,"w")
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
    for h in range(len(transposed)):
        for i in range(len(transposed[h])):
            if i>0: outfile.write("|")
            outfile.write(transposed[h][i])
        outfile.write('\n')
    outfile.close()

def downloader(data,destino,index):
    tglobal=time.time()
    print "\nInitiating download process..."
    
    gspath = 'gs://m-lab/ndt/' + data + '/'
    tarlist = subprocess.check_output('gsutil ls ' + gspath, shell=True)
    tarlist = tarlist.split('\n')
    print "There are a total of %i files for this date. Working on file %i (index %i)." %(len(tarlist)-1,index+1,index)
    if index >= len(tarlist)-1 :
        raise ValueError, "This is an invalid index file. Probably, all the files for this date have been processed. Terminating the programme."
    
    chamada = 'gsutil cp ' + tarlist[index] + " " + destino
    subprocess.call(chamada, shell=True)
    
    fpath = tarlist[index]
    fname = fpath.split("/")
    fname = str(fname[-1])
    local = destino + fname
    
    tglobal = time.time()-tglobal
    print "Total download time: " + str(tglobal) + " seconds."
    
    return local

def checkindex(data,destino,index):
    update=0
    if index == "l":
        update = 1
        try:
            indexator = open(destino+data+"/indexator.txt","r")
            index = long(indexator.read())
            indexator.close()
        except IOError:
            print "The indexator does not exist. Starting, therefore, from file index 0."
            index = 0
    return index, update

def updatedelete(update,destino,data,index,filelist,tarpath):
    if update == 1:
        indexator = open(destino+data+"/indexator.txt","w")
        index += 1
        indexator.write(str(index))
        indexator.close()
        
    for x in filelist:
        x=destino+x
        os.remove(x)
    os.remove(tarpath)

    

def roda(data,destino,index):
    troda=time.time()
    
    index,update = checkindex(data,destino,index)

    print "\nInitiating the program for " + data + ", file index " + str(index) + "."
    tarpath = downloader(data,destino,index)
    filelist = texpand(tarpath)
    mfilelist = metalist(filelist)

    if mfilelist == [] :
        updatedelete(update,destino,data,index,filelist,tarpath)
        return

    tester = 0
    intermediate = 0
    while intermediate == 0:
        intermediate=reader(destino+mfilelist[tester])
        tester+=1

    final={}
    for x in intermediate:
        final[x]=[]

    for x in mfilelist:
        input=destino+x
        intermediate=reader(input)
        if intermediate==0:
            continue
        for y in intermediate:
            final[y].append(intermediate[y])

    creationpath=destino+"Results/"+data+"/summary_%03i.txt" %index
    if os.path.exists(destino+"Results/"+data+"/") == False: os.makedirs(destino+"Results/"+data+"/")
    createout(creationpath,final)

    updatedelete(update,destino,data,index,filelist,tarpath)

    troda=time.time()-troda
    print "\nThe program took " + str(troda) + " seconds."

while 666 > 1:
    try: roda('2014/03/01','/Users/pedro/CTI/ID/MLab/NDT/',"l")
    except IOError:
        print "\nThere seems to have occurred an IOError. Probably, something went awry with the download. Let us give it another try"
        continue
    except ValueError:
        print "\nThis is an invalid index file. Probably, all the files for this date have been processed. Terminating the programme. This is probably the end, mate, start working on another date!!"
        break
    except KeyError:
        print "A KeyError, you don't say? This should nay have happened. It matters not: let us merely run this shit again."
        continue

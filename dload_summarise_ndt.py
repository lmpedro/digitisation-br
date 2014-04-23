# -*- coding: utf-8 -*-

'''
This program downloads NDT test files, unpacks them and creates summary files for each tarball. These summaries are |-separated files, with a test per line. It only gathers information available in the .meta files, and organises it in a variable per line. The data collected in the heading "Summary data" goes into 53 variables, sequentially named web100_3... web100_55.
It defines the function dload_summarise().
'''

import codecs
import time
import os
import zipfile
import tarfile
import csv
import subprocess

#parses a file path, returning its name and directory.
def parser(input):
    inpath=""
    temppath=input.split("/")
    for x in range(len(temppath)-1):
        inpath+=str(temppath[x])+"/"
    
    tempname=temppath[-1].split(".")
    inname=tempname[-2]

    return inpath,inname

#Receives a .meta file and returns it as a dictionary
#Each dict heading has a single entry
#The dict headings are the various entries in the input file
#The "summary data" heading is replaced by web100_3 ... web100_55
#All "Additional data" are discarded
#Files with incomplete Summary data (<53 entries) are discarded (returns 0)
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

#Expands an input tarfile and returns a list with the paths of all extracted files
def texpand(input):
    ttotal=time.time()
    tfil=time.time()
    print "\nExtracting filenames..."
    
    targuy=tarfile.open(input,"r")
    namelist=targuy.getnames()
    tfil=time.time()-tfil
    print "Extracted filenames in: ",tfil," seconds."
    
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

#Returns a list with the paths of all .meta files
#These are the files that must be used to create the summaries
#Receives a list of file paths as input
def metalist(input):
    output=[]
    for x in input:
        jon = x.split(".")
        if jon[-1]=="meta": output.append(x)
    
    return output

#Creates a summary file from a dict with many headings and, in each of them, a list of equal length
#In practical terms, it receives the final dictionary with the data present in all metafiles of the tarball
#Does not return anything, just creates the file
#Receives (as output) the path of the file to be created
#The file is |-separated, with \n as eol character.
def createout(output,input):
    print "\nCreating summary file..."
    outfile = open(output,"w")
    transposed = dict_to_tlist(input)
    for h in range(len(transposed)):
        for i in range(len(transposed[h])):
            if i>0: outfile.write("|")
            outfile.write(transposed[h][i])
        outfile.write('\n')
    outfile.close()

#This is a particularly stupid piece of code, which became necessary due to an initial choice that I chose not to work around.
#It receives a dictionary with X headings, each with a list of length N=constant.
#Returns this dictionary as a list, with sorted headings as the first row and observations following.
def dict_to_tlist(input):
    i = 0
    listed = []
    sortee = sorted(input)
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

    return transposed

#Downloads a tarfile from NDT, which is stored in Google Storage.
#It receives an index to show which file to download.
#By attempting to download a file with an index higher than the number of available files, it issues a message and exits.
#Besides downloading a tarball, it returns its location.
#Receives the date for which to download, the destination of tarball and the index number.
def downloader(data,destino,index):
    tglobal=time.time()
    print "\nInitiating download process..."
    
    gspath = 'gs://m-lab/ndt/' + data + '/'
    exitcode = 0
    while exitcode == 0:
        try:
            tarlist = subprocess.check_output('gsutil ls ' + gspath, shell=True)
            exitcode = 1
        except CalledProcessError:
            print "CalledProcessError, you don't say? Let's give it another try!"
    tarlist = tarlist.split('\n')
    print "There are a total of %i files for this date. Working on file %i (index %i)." %(len(tarlist)-1,index+1,index)
    if index >= len(tarlist)-1 :
        raise ValueError, "This is an invalid index file. Probably, all the files for this date have been processed. Terminating the programme."
    
    chamada = 'gsutil cp ' + tarlist[index] + " " + destino
    exitcode = 0
    while exitcode == 0:
        try:
            subprocess.call(chamada, shell=True)
            exitcode = 1
        except CalledProcessError:
            print "CalledProcessError, you don't say? Let's give it another try!"

    fpath = tarlist[index]
    fname = fpath.split("/")
    fname = str(fname[-1])
    local = destino + fname
    
    tglobal = time.time()-tglobal
    print "Total download time: " + str(tglobal) + " seconds."
    
    return local

#Except if index != "l", reads the number of the last downloaded file and indicates that it should be updated later
#If index != "l", it was defined by the user as a different value that directly indicates the file to be downloaded
#In this case, returns the same index number indicated by the user and says that the indexator file should not be updated.
#Receives the date and the directory of the indexator file.
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

#Updates the indexator file and deletes a bunch of stuff.
#Deletes all files in the tarball and the tarball itself.
#Receives the update-indicator, the directory of the indexator file, the date, the index number, the list of paths of the files extracted from the tarball and the path of the tarball.
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

#Receives the date as user input
#Asserts it is >2009/01/01 and <2014/12/31
#Asserts if follows the pattern YYYY/MM/DD
#Returns the date as a string and a list with year, month and day
def getdate():
    date = raw_input()
    
    datelist=date.split('/')
    year=datelist[0]
    month=datelist[1]
    day=datelist[2]
    
    assert int(year)>=2009 and int(year)<=2014 and len(year)==4
    assert int(month)>=1 and int(month)<=12 and len(month)==2
    assert int(day)>=1 and int(day)<=31 and len(day)==2
    
    return date, datelist

#Asks if the user wants to download a single file or not.
#If s/he so wishes, the whole program will run only once.
#Receives nothing, returns the proper index.
def getindex():
    index = raw_input()

    assert index=="y" or index=="Y" or index=="n" or index=="N"

    if index=="y" or index=="Y":
        index = "l"
    else:
        print "Enter the number of the file your heart desires, then:"
        index = int(raw_input())

        assert isinstance(index,int)
    
    return index

#The main program. Downloads, extracts, resumes and deletes.
#Receives the date, the base directory to use and the index indicator (="l" for the downloading the first unworked file).
def roda(data,destino,index):
    troda=time.time()
    
    index,update = checkindex(data,destino,index)
    
    print "\nInitiating the program for " + data + ", file index " + str(index) + "."
    tarpath = downloader(data,destino,index)
    filelist = texpand(tarpath)
    mfilelist = metalist(filelist)
    
    if mfilelist == [] :
        updatedelete(update,destino,data,index,filelist,tarpath)
        print "No valid metafiles for this date and server, bloke!"
        return
    
    tester = 0
    intermediate = 0
    while intermediate == 0:
        try:
            intermediate=reader(destino+mfilelist[tester])
            tester+=1
        except IndexError:
            updatedelete(update,destino,data,index,filelist,tarpath)
            print "No valid metafiles for this date and server, bloke!"
            return
    
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

#The whole thing. Enters a semi-eternal loop, dloading file after file and doing the proper processing.
#This will only be ran to its end on the rarest of occasions, as each day has got approximately 50 GB of data.
#Receives nothing, returns nothing.
#Asks user for the date and whether s/he wants to continue from the last downloaded file.
def dload_summarise():
    print "Enter date (YYYY/MM/DD):"
    date, datelist = getdate()
    print "Do you fancy continuing from the last downloaded file? (Y/N)"
    index = getindex()

    while 666 > 1:
        try:
            roda(date,'/Users/pedro/CTI/ID/MLab/NDT/',index)
            if index!="l": break
        except IOError:
            print "\nThere seems to have occurred an IOError. Probably, something went awry with the download. Let us give it another try"
            continue
        except ValueError:
            print "\nThis is an invalid index file. Probably, all the files for this date have been processed. Terminating the programme. This is probably the end, mate, start working on another date!!"
            return
        except KeyError:
            print "A KeyError, you don't say? This should nay have happened. It matters not: let us merely run this shit again."
            continue

dload_summarise()

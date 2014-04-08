# -*- coding: utf-8 -*-

'''
    This program defines the function gf_ndt().
    It is intended to work after the elsewhere defined function dload_summarise_ndt(), which dloads and creates summaries of NDT tests. Our present concern reads these various summary files for a single date and creates a |-delimited file with all tests for Brazil. Besides the information present in the NDT tests, it includes geolocation data: city name, city code (I am not aware of which coding system this would be, but we can find about it in the MLab NDT wiki), latitude and longitude. Not all of these four fields are necessarily available for every observation.
    Finally, this program begins by receivng input from the user (date, number of files to be read and output path).
'''

import time
import os
import maxminddb as geo
import socket
import io

def localizer(geo,IP):
    try:
        location = geo.get(IP)
        x = IP
    except ValueError:
        try:
            x = socket.gethostbyname(IP)
            location = geo.get(x)
        except socket.gaierror:
            location = ''
            x = ''
    return location, x

def falsedic(entry,list):
    i = 0
    for x in list:
        if x == entry: return i
        i+=1
    raise ValueError

def setcount(list):
    lset = set(list)
    countdic = {}
    for x in lset:
        countdic[x] = 0
    for x in list:
        countdic[x] += 1
    return countdic

def reducegeo(geo):
    reduced=[]
    try:
        reduced.append(geo["city"]["geoname_id"])
    except KeyError:
        reduced.append('')
    try:
        reduced.append(geo["city"]["names"]["pt-BR"])
    except KeyError:
        reduced.append('')
    try:
        reduced.append(geo["location"]["latitude"])
    except KeyError:
        reduced.append('')
    try:
        reduced.append(geo["location"]["longitude"])
    except KeyError:
        reduced.append('')
    return reduced

def brazilianiser(tests, geoobject,br):
    counter=[0,0]
    clist=[]
    btests=[]
    geoindex = falsedic("client IP address",tests[0])
    for j in range(len(tests)):
        place, red_ip = localizer(geoobject,tests[j][geoindex])
        if place == '' or place == None:
            counter[1]+=1
        else:
            try:
                clist.append(place["country"]["iso_code"])
                if place["country"]["iso_code"] == "BR":
                    br+=1
                    btests.append(tests[j])
                    btests[-1].append(red_ip)
                    rplace=reducegeo(place)
                    for x in rplace:
                        btests[-1].append(x)
                counter[0] += 1
            except TypeError:
                print "There was a TypeError, you see."
                counter[1] += 1
                print place
            except KeyError:
                print "There was a KeyError, you see."
                counter[1] += 1
                print place
    print "\nSo far, br is "+str(br)
    print "So for our clist, ..."
    clistcounted = setcount(clist)
    print clistcounted
    print "We have had %i %i hits and misses." % (counter[0], counter[1])
    return btests, br, counter

def createout(output,input,header):
    print "\nCreating summary file..."
    outfile = io.open(output,"w",encoding='utf8')
    #total=header+input
    header.append("true_IP")
    header.append("city_geoname_id")
    header.append("city_name")
    header.append("latitude")
    header.append("longitude")
    total = []
    total.append(header)
    for x in input:
        total.append(x)
    i=0
    for h in range(len(total)):
        for i in range(len(total[h])):
            if i>0: outfile.write(u"|")
            outfile.write(unicode(total[h][i]))
        outfile.write(u'\n')
    outfile.close()

def checkoutput(input):
    if os.path.exists(input):
        print "The summary file to be created already exists. Do you want it to be overwritten? (Y/N)"
        ovw = raw_input()
        assert ovw=="y" or ovw=="Y" or ovw=="n" or ovw=="N"
        if ovw=="y" or ovw == "Y":
            return input
        else:
            newpath = input
            while os.path.exists(newpath):
                print "Then please let us know the path of the file to be created, mate (no commas, please)."
                newpath = raw_input()
            return newpath
    else:
        print "\nOk, the summary file does not exist! It shall be crafted to the best of our skills."
        return input

def getdate():
    print "Enter date (YYYY/MM/DD):"
    date = raw_input()
    
    datelist=date.split('/')
    year=datelist[0]
    month=datelist[1]
    day=datelist[2]
    
    assert int(year)>=2009 and int(year)<=2014 and len(year)==4
    assert int(month)>=1 and int(month)<=12 and len(month)==2
    assert int(day)>=1 and int(day)<=31 and len(day)==2
    
    return date, datelist

def readsum(input):
    file = open(input,"r")
    tests = []
    for x in file:
        tests.append(x.split("|"))
    
    file.close()
    if tests[0]==['\n']: del tests[0]
    for x in range(len([tests[0]])):
        if tests[0][x]=='': del tests[0][x]
    for h in range(len(tests)):
        for i in range(len(tests[h])):
            tests[h][i]=tests[h][i].replace('\n','')
            

    return tests

def testsprocessor(input, rdirectory, gi, br, btests, hitmiss):
    filetime = time.time()
    tests=readsum(rdirectory+input)
    
    inttest, br, phitmiss = brazilianiser(tests,gi,br)
    hitmiss[0] += phitmiss[0]
    hitmiss[1] += phitmiss[1]
    if inttest!=[]:
        for x in range(len(inttest)):
            btests.append(inttest[x])
    filetime = time.time()-filetime
    print "%i tests in %i seconds. Average number of tests per second: %.1f." % (len(tests),filetime,(len(tests)/filetime))

    return br, btests, tests, hitmiss

def getindex():
    print "Would you like to read but a couple of summaries? (y/n)?"
    ans = raw_input()
    assert ans=="y" or ans=="Y" or ans=="n" or ans=="N"
    if ans == "n" or ans == "N":
        return 0,999999
    else:
        print "Then disclose the first file you'd rather get purchase on:"
        llim = int(raw_input())
        print "As for the last one, which will it be?"
        ulim = int(raw_input())
        assert isinstance(llim,int) and isinstance(ulim,int)
        return llim, ulim

def setentries():
    database="/Users/pedro/CTI/ID/GeoLite2 dloaded march 12/GeoLite2-City.mmdb"
    
    gi = geo.Reader(database)
    
    basepath="/Users/pedro/CTI/ID/MLab/NDT/Results/"
    
    date, datelist = getdate()
    
    llim, ulim = getindex()
    
    finalcsv="/Users/pedro/CTI/ID/MLab/NDT/Results/BR/%s%s%s_brsum.txt" %(datelist[0], datelist[1], datelist[2])
    
    finalcsv = checkoutput(finalcsv)
    
    rdirectory = basepath+date+"/"
    
    rlist = cleanlist(os.listdir(rdirectory))
    
    br=0
    btests=[]
    counter=0
    hitmiss=[0,0]
    
    if ulim == 999999 : nfiles = len(rlist)
    else: nfiles = ulim - llim + 1

    return gi, date, datelist, llim, ulim, finalcsv, rdirectory, rlist, br, btests, counter, hitmiss, nfiles

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

def gf_ndt():
    totaltime = time.time()
    
    gi, date, datelist, llim, ulim, finalcsv, rdirectory, rlist, br, btests, counter, hitmiss, nfiles = setentries()

    for summary in rlist:
        if counter < llim:
            counter +=1
            continue
        if counter > ulim: break
        counter+=1
        br, btests, tests, hitmiss = testsprocessor(summary, rdirectory, gi, br, btests, hitmiss)
        print "We finished file %s. There are %i files." % (summary,len(rlist))

    createout(finalcsv,btests,tests[0])
    totaltime = time.time() - totaltime
    print "The program has ended. We have read %i files. This led to %i tests with a %.2f hit rate, over %i minutes. This gives us an average rate of %.1f tests per second." % (nfiles, hitmiss[0] + hitmiss[1], float(hitmiss[0])/(hitmiss[0] + hitmiss[1]), totaltime/60, float((hitmiss[0] + hitmiss[1]))/totaltime)

gf_ndt()
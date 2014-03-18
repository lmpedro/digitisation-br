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
                    red_ip = [red_ip]
                    btests.append(red_ip)
                    rplace=reducegeo(place)
                    for x in rplace:
                        btests[-1].append(x)
                    print btests[-1]
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
    return btests, br

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
    print total
    for h in range(len(total)):
        for i in range(len(total[h])):
            if i>0: outfile.write(u"|")
            print total[h][i]
            outfile.write(unicode(total[h][i]))
        outfile.write(u'\n')
    outfile.close()

database="/Users/pedro/CTI/ID/GeoLite2 dloaded march 12/GeoLite2-City.mmdb"

gi = geo.Reader(database)

basepath="/Users/pedro/CTI/ID/MLab/NDT/Results/"
data="2014/03/01"
rdirectory = basepath+data+"/"

rlist = os.listdir(rdirectory)

br=0
btests=[]
joe=0
for summary in rlist:
    if joe>10:break
    if joe<9:
        joe+=1
        continue
    filetime = time.time()
    file = open(rdirectory+summary,"r")

    tests = []
    for x in file:
        tests.append(x.split("|"))

    file.close()

    for h in range(len(tests)):
        for i in range(len(tests[h])):
            tests[h][i]=tests[h][i].replace('\n','')

    inttest, br = brazilianiser(tests,gi,br)
    if inttest!=[]:
        for x in range(len(inttest)):
            btests.append(inttest[x])
    filetime = time.time()-filetime
    print "%i tests in %i seconds. Average number of tests per second: %.1f." % (len(tests),filetime,(len(tests)/filetime))
    print "We finished file %s. There are %i files." % (summary,len(rlist))
    joe+=1
print btests
finalcsv="/Users/pedro/CTI/ID/MLab/NDT/Results/test.txt"

createout(finalcsv,btests,tests[0])

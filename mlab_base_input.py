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
from mlab_base import parser, reader, texpand, metalist, createout, downloader, checkindex, updatedelete, roda

date = raw_input()
print date
'''
    while 666 > 1:
    try: roda('2014/03/02','/Users/pedro/CTI/ID/MLab/NDT/',"l")
    except IOError:
    print "\nThere seems to have occurred an IOError. Probably, something went awry with the download. Let us give it another try"
    continue
    except ValueError:
    print "\nThis is an invalid index file. Probably, all the files for this date have been processed. Terminating the programme. This is probably the end, mate, start working on another date!!"
    break
    except KeyError:
    print "A KeyError, you don't say? This should nay have happened. It matters not: let us merely run this shit again."
    continue
'''
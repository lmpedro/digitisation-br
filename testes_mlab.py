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


subprocess.call('gsutil cp gs://m-lab/ndt/2014/02/01/20140201T000000Z-mlab4-nuq01-ndt-0001.tgz "/Volumes/External Data/"', shell=True)
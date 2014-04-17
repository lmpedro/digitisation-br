# -*- coding: utf-8 -*-

import codecs
import time
import os
import zipfile
import tarfile
import csv
import subprocess

base="/Users/pedro/CTI/ID/Anatel/Banda Larga nas Escolas/"
list=[base+"BandaLargaNasEscolasPúblicasUrbanas.xls",
      base+"BandaLargaNasEscolasPúblicasUrbanas (1).xls",
      base+"BandaLargaNasEscolasPúblicasUrbanas (2).xls",
      ]

for x in list:
    ho=subprocess.check_output('iconv -f iso-8859-1 -t utf-8 '+'"'+x+'"', shell=True)
    file=open(x+"ccc","w")
    file.write(ho)
    file.close

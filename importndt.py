# -*- coding: utf-8 -*-

import httplib2
import pprint
import sys
import io

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from bqndt import servicer
from bqndt import runAsyncQuery

brcond='AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.country_name) AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.region) AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.city) AND connection_spec.client_geolocation.country_name="Brazil"'
condition = 'IS_EXPLICITLY_DEFINED(project) AND project = 0 AND IS_EXPLICITLY_DEFINED(connection_spec.data_direction) %s' % brcond

datelist=[]
for ano in range(2009,2015):
    if ano==2009:
        for i in range(8,13):
            datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
    elif ano==2014:
        for i in range(1,5):
            datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
    else:
        for i in range(1,13):
            datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))

qlist=[]
for date in datelist:
    qlist.append('SELECT * FROM [%s] WHERE %s' %(date, condition))


destDatasetId='ndtbr'
destTableId='combndt'
PROJECT_NUMBER = '448623832260'





FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/bigquery')

service = servicer(PROJECT_NUMBER)






#deleteTable(projectId='448623832260', service=service, datasetId=destDatasetId, tableId=destTableId)
try: deleteTable(projectId='448623832260', service=service, datasetId=destDatasetId, tableId=destTableId)
except:
    print "Iargh!"

i=0
print 'Qlist length is: %i' % (len(qlist))

for qdef in qlist:
    i+=1
    print i
    runAsyncQuery(qdef=qdef, service=service, destDatasetId=destDatasetId, destTableId=destTableId, priority='BATCH')

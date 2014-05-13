# -*- coding: utf-8 -*-

import httplib2
import pprint
import sys
import io
import time

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

from bqndt import servicer
from bqndt import runAsyncQuery
from bqndt import deleteTable
from bqndt import getTable

brcond='AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.country_name) AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.region) AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.city) AND connection_spec.client_geolocation.country_name="Brazil"'
lastentrycond = 'AND IS_EXPLICITLY_DEFINED(web100_log_entry.is_last_entry) AND web100_log_entry.is_last_entry = True'
condition = 'IS_EXPLICITLY_DEFINED(project) AND project = 0 AND IS_EXPLICITLY_DEFINED(connection_spec.data_direction) %s %s;' % (brcond, lastentrycond)

datelist=[]
for ano in reversed(range(2009,2015)):
    if ano==2009:
        for i in reversed(range(8,13)):
            datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
    elif ano==2014:
        for i in reversed(range(1,5)):
            datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
    else:
        for i in reversed(range(1,13)):
            datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))

qlist=[]
for date in datelist:
    qlist.append('SELECT * FROM [%s] WHERE %s' %(date, condition))


destDatasetId='digitisationBR'
destTableId='ndt_br'
PROJECT_NUMBER = '448623832260'





FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/bigquery')

service = servicer(PROJECT_NUMBER)



#Deletes the final table, if it exists
try: deleteTable(projectId='448623832260', service=service, datasetId=destDatasetId, tableId=destTableId)
except:
    print "Iargh!"

#Creates the intermediary tables
i=0
print 'Qlist length is: %i' % (len(qlist))
for qdef, date in zip(qlist, datelist):
    i+=1
    print i
    destTableId='ndtbr'+date[-7:][:4]+date[-2:]
    check=getTable(projectId=PROJECT_NUMBER,service=service,datasetId=destDatasetId,tableId=destTableId)
    if check == None:
        runAsyncQuery(qdef=qdef, service=service, destDatasetId=destDatasetId, destTableId=destTableId, priority='BATCH', writeDisposition='WRITE_EMPTY')
        time.sleep(120)

#Creates the final table
qdef="SELECT * FROM (TABLE_QUERY(ndtexplorer:digitisationBR,'table_id CONTAINS \"ndtbr\"'))"
destTableId='ndt_br'
runAsyncQuery(qdef=qdef, service=service, destDatasetId=destDatasetId, destTableId=destTableId, priority='BATCH', writeDisposition='WRITE_EMPTY')

#Deletes the intermediary tables created
for qdef, date in zip(qlist, datelist):
    i+=1
    print i
    destTableId='ndtbr'+date[-7:][:4]+date[-2:]
    deleteTAble(service=service, projectId=PROJECT_NUMBER DatasetId=destDatasetId, TableId=destTableId)
    time.sleep(10)

# -*- coding: utf-8 -*-

import httplib2
import pprint
import sys
import io
import subprocess

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run



def DefQlist(onequery=1, early=1):

    geovar= 'connection_spec_client_geolocation_region AS region, connection_spec_client_geolocation_city AS city, connection_spec_client_geolocation_latitude AS lat, connection_spec_client_geolocation_longitude AS lon'
    basicvars= 'web100_log_entry_connection_spec_remote_ip AS ip_remote, web100_log_entry_connection_spec_local_ip AS ip_local, test_id AS test_id, STRFTIME_UTC_USEC(UTC_USEC_TO_DAY(web100_log_entry_log_time * 1000000), "%Y%m%d") AS day, connection_spec_client_browser AS browser'
    lastentrycond = 'IS_EXPLICITLY_DEFINED(web100_log_entry_is_last_entry) AND web100_log_entry_is_last_entry = True'
    dtimecond='IS_EXPLICITLY_DEFINED(web100_log_entry_snap_HCThruOctetsAcked) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SndLimTimeRwin) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SndLimTimeCwnd) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SndLimTimeSnd) AND web100_log_entry_snap_HCThruOctetsAcked >= 8192 AND (web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd) >= 9000000 AND (web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd) < 3600000000'
    ipcond='IS_EXPLICITLY_DEFINED(web100_log_entry_connection_spec_remote_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry_connection_spec_local_ip)'
    udirection='IS_EXPLICITLY_DEFINED(connection_spec_data_direction) AND connection_spec_data_direction = 0'
    ddirection='IS_EXPLICITLY_DEFINED(connection_spec_data_direction) AND connection_spec_data_direction = 1'
    if early:
        earlycondition='web100_log_entry_log_time>1325376000'
    else:
        earlycondition='web100_log_entry_log_time>1'

    condition=[
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CongSignals) AND web100_log_entry_snap_CongSignals > 0 AND %s AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection, earlycondition),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_HCThruOctetsReceived) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_Duration) AND web100_log_entry_snap_HCThruOctetsReceived >= 8192 AND web100_log_entry_snap_Duration >= 9000000 AND web100_log_entry_snap_Duration < 3600000000 AND %s AND %s AND %s' % (ipcond, lastentrycond, udirection, earlycondition),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_MinRTT) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CountRTT) AND web100_log_entry_snap_CountRTT > 0 AND %s AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection, earlycondition),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SumRTT) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CountRTT) AND web100_log_entry_snap_CountRTT > 10 AND %s AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection, earlycondition),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SegsRetrans) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_DataSegsOut) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CongSignals) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_DupAcksIn) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_DataSegsIn) AND %s AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection, earlycondition),
               ]

    varselect=[
               '(web100_log_entry_snap_HCThruOctetsAcked/(web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd)) AS dspeed, (web100_log_entry_snap_SndLimTimeCwnd/(web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd)) AS netlimited, (web100_log_entry_snap_SndLimTimeRwin/(web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd)) AS rcvlimited, %s, %s ' % (geovar, basicvars),
               'web100_log_entry_snap_HCThruOctetsReceived/web100_log_entry_snap_Duration AS uspeed, %s, %s ' % (geovar, basicvars),
               'web100_log_entry_snap_MinRTT AS minrtt, %s, %s ' % (geovar, basicvars),
               '(web100_log_entry_snap_SumRTT/web100_log_entry_snap_CountRTT) AS avgrtt, %s, %s ' % (geovar, basicvars),
               'web100_log_entry_snap_SegsRetrans/web100_log_entry_snap_DataSegsOut AS pktretrans, web100_log_entry_snap_CongSignals/web100_log_entry_snap_DataSegsOut AS pktloss, web100_log_entry_snap_DupAcksIn/web100_log_entry_snap_DataSegsIn AS pktooo, %s, %s ' % (geovar, basicvars),
               ]

    qlist=[]
    if onequery:
        qlist.append('SELECT %s FROM [ndtexplorer:digitisationBR.ndt_br] WHERE %s;' % (varselect[0], condition[0]))
    else:
        for x, y in zip(varselect, condition):
            qlist.append('SELECT %s FROM [ndtexplorer:digitisationBR.ndt_br] WHERE %s;' % (x, y))

    return qlist



def servicer(projectId):
    storage = Storage('bigquery_credentials.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        from oauth2client import tools
        # Run oauth2 flow with default arguments.
        credentials = tools.run_flow(FLOW, storage, tools.argparser.parse_args([]))

    http = httplib2.Http()
    http = credentials.authorize(http)

    bigquery_service = build('bigquery', 'v2', http=http)
    
    return bigquery_service



def printTableData(data, startIndex):
  for row in data['rows']:
    rowVal = []
    for cell in row['f']:
        rowVal.append(cell['v'])
    print 'Row %d: %s' % (startIndex, rowVal)
    startIndex +=1




# Run a synchronous query, save the results to a table, overwriting the
# existing data, and print the first page of results.
# Default timeout is to wait until query finishes.
def runSyncQuery (qdef, service, projectId='448623832260', timeout=0,verbose=0,giveback=0):
  try:
    print 'timeout:%d' % timeout
    
    jobCollection = service.jobs()
    queryData = {'query':qdef,'timeoutMs':timeout}

    queryReply = jobCollection.query(projectId=projectId,
                                     body=queryData).execute()

    jobReference=queryReply['jobReference']

    # Timeout exceeded: keep polling until the job is complete.
    while(not queryReply['jobComplete']):
      print 'Job not yet complete...'
      queryReply = jobCollection.getQueryResults(
                          projectId=jobReference['projectId'],
                          jobId=jobReference['jobId'],
                          timeoutMs=timeout).execute()
    if verbose:
        # If the result has rows, print the rows in the reply.
        if('rows' in queryReply):
          print 'has a rows attribute'
          printTableData(queryReply, 0)
          currentRow = len(queryReply['rows'])

          # Loop through each page of data
          while('rows' in queryReply and currentRow < queryReply['totalRows']):
            queryReply = jobCollection.getQueryResults(
                              projectId=jobReference['projectId'],
                              jobId=jobReference['jobId'],
                              startIndex=currentRow).execute()
            if('rows' in queryReply):
              printTableData(queryReply, currentRow)
              currentRow += len(queryReply['rows'])

    print "Job Complete! Its project is %s, its ID %s. There are %s rows." % (jobReference['projectId'], jobReference['jobId'], queryReply['totalRows'])

    if giveback==1:
        return jobReference
    elif giveback==2:
        queryReply = jobCollection.getQueryResults(
                                                   projectId=jobReference['projectId'],
                                                   jobId=jobReference['jobId']).execute()
        return jobReference, queryReply
    

  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
    "the application to re-authorize")

  except HttpError as err:
    print 'Error in runSyncQuery:', pprint.pprint(err.content)

  except Exception as err:
    print 'Undefined error'
    print err



def viewSyncQuery(jobId, service, projectId='448623832260', timeout=0, verbose=1, giveback=0):
  try:
    print 'timeout:%d' % timeout
    
    jobCollection = service.jobs()

    queryReply = jobCollection.getQueryResults(projectId=projectId,
                                     jobId=jobId).execute()

    jobReference=queryReply['jobReference']

    # Timeout exceeded: keep polling until the job is complete.
    while(not queryReply['jobComplete']):
      print 'Job not yet complete...'
      queryReply = jobCollection.getQueryResults(
                          projectId=jobReference['projectId'],
                          jobId=jobReference['jobId'],
                          timeoutMs=timeout).execute()
    if verbose:
        # If the result has rows, print the rows in the reply.
        if('rows' in queryReply):
          print 'has a rows attribute'
          printTableData(queryReply, 0)
          currentRow = len(queryReply['rows'])

          # Loop through each page of data
          while('rows' in queryReply and currentRow < queryReply['totalRows']):
            queryReply = jobCollection.getQueryResults(
                              projectId=jobReference['projectId'],
                              jobId=jobReference['jobId'],
                              startIndex=currentRow).execute()
            if('rows' in queryReply):
              printTableData(queryReply, currentRow)
              currentRow += len(queryReply['rows'])

    if giveback:
        queryReply = jobCollection.getQueryResults(
                                                 projectId=jobReference['projectId'],
                                                 jobId=jobReference['jobId']).execute()
        return queryReply

  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
    "the application to re-authorize")

  except HttpError as err:
    print 'Error in runSyncQuery:', pprint.pprint(err.content)

  except Exception as err:
    print 'Undefined error: %s' % err
    print err




def getTable(service, projectId, datasetId, tableId, verbose=0):
  tableCollection = service.tables()
  try:
    tableReply = tableCollection.get(projectId=projectId,
                                   datasetId=datasetId,
                                   tableId=tableId).execute()
    if verbose:
        print 'Printing table resource %s:%s.%s' % (projectId, datasetId, tableId)
        pprint.pprint(tableReply)
    return tableReply

  except HttpError as err:
    print 'Error in querytableData: ', pprint.pprint(err)
    return None





def runAsyncQuery (qdef, service, projectId='448623832260', destProjectId='448623832260', destDatasetId='', destTableId='', writeDisposition='WRITE_APPEND', priority='INTERACTIVE', allowLargeResults=False):
  try:
    jobCollection = service.jobs()
    queryString = qdef+';'
    if destDatasetId!='':
        jobData = {
            'configuration': {
                'query': {
                    'query': qdef,
                    'destinationTable': {
                        'projectId': destProjectId,
                        'datasetId': destDatasetId,
                        'tableId': destTableId
                    },
                    'writeDisposition': writeDisposition,
                    'priority': priority,
                    'allowLargeResults': allowLargeResults,
                }
            }
        }
    else:
        jobData = {
          'configuration': {
            'query': {
                'query': qdef,
                'priority': priority,
            }
          }
        }

    insertResponse = jobCollection.insert(projectId=projectId,
                                         body=jobData).execute()

    return insertResponse

  except HttpError as err:
    print 'Error in runAsyncTempTable:', pprint.pprint(err.resp)

  except Exception as err:
    print 'Undefined error' % err





def deleteTable(service, datasetId, tableId, projectId='448623832260'):
    service.tables().delete(projectId=projectId,
                            datasetId=datasetId,
                            tableId=tableId).execute()







def outputter(outpath, input):
    output = io.open(outpath,"w")
    
    header=[]
    for x in input['schema']['fields']:
        header.append(x['name'])
    
    print header

    final=[]
    final.append(header)
    for row in input['rows']:
        rowVal = []
        for cell in row['f']:
            rowVal.append(cell['v'])
        final.append(rowVal)

    for h in range(len(final)):
        for i in range(len(final[h])):
            if i>0: output.write(u"|")
            output.write(unicode(final[h][i]))
        output.write(u'\n')
    output.close()







def exportTable(service, projectId, datasetId, tableId, destFile, bucket='ndttostata'):

  url = "https://www.googleapis.com/bigquery/v2/projects/" + projectId + "/jobs"

  jobCollection = service.jobs()
  jobData = {
    'projectId': projectId,
    'configuration': {
      'extract': {
        'sourceTable': {
           'projectId': projectId,
           'datasetId': datasetId,
           'tableId': tableId
         },
        'destinationUris': ['gs://%s/%s' %(bucket, destFile)],
       }
     }
   }
  insertJob = jobCollection.insert(projectId=projectId, body=jobData).execute()
  import time
  while True:
    status =jobCollection.get(projectId=projectId, jobId=insertJob['jobReference']['jobId']).execute()
    print status
    if 'DONE' == status['status']['state']:
      print "Done exporting!"
      return
    print 'Waiting for export to complete..'
    time.sleep(10)





def schemaCreator(input):
    filename=input.split('.')[-2]
    subline='iconv -f macroman -t utf-8 \"%s\"' % (input)
    converted=subprocess.check_output(subline,shell=True).split('\n')

    helpingHand={}
    i=0
    for x in converted:
        i+=1
        x=x.split('|')
        x[-1]=x[-1].replace('\n','')
        helpingHand[i]=x

    fields=[]
    for x,y,z in zip(helpingHand[1],helpingHand[2],helpingHand[3]):
        oneField={}
        oneField['name']=x
        oneField['description']=y
        oneField['type']=z
        fields.append(oneField)
    return fields







def loadTable(service, projectId, datasetId, targetTableId, sourceCSV, fields):
  try:
    jobCollection = service.jobs()
    jobData = {
      'projectId': projectId,
      'configuration': {
          'load': {
            'fieldDelimiter': '|',
            'sourceUris': [sourceCSV],
            'schema': {
              'fields': fields
            },
            'destinationTable': {
              'projectId': projectId,
              'datasetId': datasetId,
              'tableId': targetTableId
            },
            'skipLeadingRows': 1,
            'sourceFormat':'CSV',
          }
        }
      }

    insertResponse = jobCollection.insert(projectId=projectId,
                                         body=jobData).execute()

    # Ping for status until it is done, with a short pause between calls.
    import time
    while True:
      job = jobCollection.get(projectId=projectId,
                                 jobId=insertResponse['jobReference']['jobId']).execute()
      if 'DONE' == job['status']['state']:
          print 'Done Loading!'
          return

      print 'Waiting for loading to complete...'
      time.sleep(10)

    if 'errorResult' in job['status']:
      print 'Error loading table: ', pprint.pprint(job)
      return

  except HttpError as err:
    print 'Error in loadTable: ', pprint.pprint(err.resp)








def mainQueriesRun(service, projectId):
    ident=['dspeed',
           'uspeed',
           'avgrtt',
           'minrtt',
           'pkts',
           ]
    destDatasetId='digitisationBR'



    qlist=DefQlist(onequery=0, early=False)

    jobdeflist=[]
    for definition,destTableId in zip(qlist,ident):
        jobdeflist.append(runSyncQuery(qdef=definition,projectId=projectId, service=service,timeout=5000, verbose=0, giveback=1))
        #runAsyncQuery(qdef=definition,projectId=projectId, service=service,destProjectId=projectId,destDatasetId=destDatasetId, destTableId=destTableId,writeDisposition='WRITE_TRUNCATE',priority='BATCH',allowLargeResults=True)

    file=open("/users/pedro/desktop/testdel.txt","w")
    i=1
    for jack in jobdeflist:
        if i>1: file.write('\n')
        file.write(jack['jobId'])
        i+=1
    file.close










def mainQueriesReadLocal(service, projectId):
    file=open("/users/pedro/desktop/testdel.txt","r")
    jobdeflist=[]
    for x in file:
        x=x.replace("\n","")
        jobdeflist.append(x)
    file.close

    basepath="/Users/pedro/CTI/ID/MLab/NDT/BigQuery/Results/Tests/"

    for definition in jobdeflist:
        result=viewSyncQuery(projectId=projectId, jobId=definition, service=service, giveback=1, verbose=0)
        path=basepath+definition+'.txt'
        outputter(path,result)
    





def mainExtracts(service, projectId):

    ident=['dspeed',
           'uspeed',
           'avgrtt',
           'minrtt',
           'pkts',
           ]
    datasetId='digitisationBR'
    
    for tableId in ident:
        exportTable(service=service, projectId=projectId, datasetId=datasetId, tableId=tableId, destFile=tableId+'.csv')






if __name__ == '__main__':

    # Enter your Google Developer Project number
    projectId = '448623832260'
    ourdataset='digitisationBR'
    object='ID_unified'
    bucket='statatodigi'
    uri='gs://%s/%s_gs.csv' % (bucket, object)
    inputInfo='/Users/pedro/CTI/ID/Statas/%s_info.csv' % object

    FLOW = flow_from_clientsecrets('client_secrets.json',
                                   scope='https://www.googleapis.com/auth/bigquery')

    service = servicer(projectId)

    #mainQueriesRun(service=service, projectId=projectId)

    #mainQueriesRun(service=service, projectId=projectId)

    #mainExtracts(service=service, projectId=projectId)
    
    fields=schemaCreator(inputInfo)
    
    loadTable(service=service, projectId=projectId, datasetId=ourdataset, targetTableId=object, sourceCSV=uri, fields=fields)


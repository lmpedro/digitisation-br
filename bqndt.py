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



def DefQlist(onequery=1):

    geovar= 'connection_spec_client_geolocation_region AS region, connection_spec_client_geolocation_city AS city, connection_spec_client_geolocation_latitude AS lat, connection_spec_client_geolocation_longitude AS lon'
    basicvars= 'web100_log_entry_connection_spec_remote_ip AS ip_remote, web100_log_entry_connection_spec_local_ip AS ip_local, test_id AS test_id, STRFTIME_UTC_USEC(UTC_USEC_TO_DAY(web100_log_entry_log_time * 1000000), "%Y-%m-%d") AS day, connection_spec_client_browser AS browser'
    lastentrycond = 'IS_EXPLICITLY_DEFINED(web100_log_entry_is_last_entry) AND web100_log_entry_is_last_entry = True'
    dtimecond='IS_EXPLICITLY_DEFINED(web100_log_entry_snap_HCThruOctetsAcked) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SndLimTimeRwin) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SndLimTimeCwnd) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SndLimTimeSnd) AND web100_log_entry_snap_HCThruOctetsAcked >= 8192 AND (web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd) >= 9000000 AND (web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd) < 3600000000'
    ipcond='IS_EXPLICITLY_DEFINED(web100_log_entry_connection_spec_remote_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry_connection_spec_local_ip)'
    udirection='IS_EXPLICITLY_DEFINED(connection_spec_data_direction) AND connection_spec_data_direction = 0'
    ddirection='IS_EXPLICITLY_DEFINED(connection_spec_data_direction) AND connection_spec_data_direction = 1'

    condition=[
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CongSignals) AND web100_log_entry_snap_CongSignals > 0 AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_HCThruOctetsReceived) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_Duration) AND web100_log_entry_snap_HCThruOctetsReceived >= 8192 AND web100_log_entry_snap_Duration >= 9000000 AND web100_log_entry_snap_Duration < 3600000000 AND %s AND %s' % (ipcond, lastentrycond, udirection),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_MinRTT) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CountRTT) AND web100_log_entry_snap_CountRTT > 0 AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SumRTT) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CountRTT) AND web100_log_entry_snap_CountRTT > 10 AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection),
               '%s AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_SegsRetrans) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_DataSegsOut) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_CongSignals) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_DupAcksIn) AND IS_EXPLICITLY_DEFINED(web100_log_entry_snap_DataSegsIn) AND %s AND %s AND %s' % (ipcond, lastentrycond, dtimecond, ddirection),
               ]

    varselect=[
               '(web100_log_entry_snap_HCThruOctetsAcked/(web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd)) AS dspeed, (web100_log_entry_snap_SndLimTimeCwnd/(web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd)) AS netlimited, (web100_log_entry_snap_SndLimTimeRwin/(web100_log_entry_snap_SndLimTimeRwin + web100_log_entry_snap_SndLimTimeCwnd + web100_log_entry_snap_SndLimTimeSnd)) AS rcvlimited, %s, %s ' % (geovar, basicvars),
               'web100_log_entry_snap_HCThruOctetsReceived/web100_log_entry_snap_Duration AS uspeed, %s, %s ' % (geovar, basicvars),
               'web100_log_entry_snap_MinRTT AS minrtt, %s, %s ' % (geovar, basicvars),
               '(web100_log_entry_snap_SumRTT/web100_log_entry_snap_CountRTT) AS avgrtt, %s, %s ' % (geovar, basicvars),
               'web100_log_entry_snap_SegsRetrans/web100_log_entry_snap_DataSegsOut AS pktretrans, web100_log_entry_snap_DataSegsOut/web100_log_entry_snap_CongSignals AS pktloss, web100_log_entry_snap_DupAcksIn/web100_log_entry_snap_DataSegsIn AS pktooo, %s, %s ' % (geovar, basicvars),
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


if __name__ == '__main__':

    # Enter your Google Developer Project number
    PROJECT_NUMBER = '448623832260'

    FLOW = flow_from_clientsecrets('client_secrets.json',
                                   scope='https://www.googleapis.com/auth/bigquery')

    service = servicer(PROJECT_NUMBER)


    #jobId='job_ouivGD0WVYFGCSUFRotpBILxoNc'
    #jobReference=runSyncQuery(qdef=qdef[1],projectId=PROJECT_NUMBER, service=service,timeout=5000)

    #data=viewSyncQuery(projectId=jobReference['projectId'], jobId=jobReference['jobId'], service=service, giveback=1)
    #data=viewSyncQuery(projectId=PROJECT_NUMBER, jobId=jobId, service=service, giveback=1)

    #outputter('/Users/pedro/desktop/aaa.txt',data)

    #a,b=runSyncQuery(qdef=qdef[-1],projectId=PROJECT_NUMBER, service=service,timeout=5000, verbose=1, giveback=2)









    qlist=DefQlist(onequery=0)

    jobdeflist=[]
    for definition in qlist:
        jobdeflist.append(runSyncQuery(qdef=definition,projectId=PROJECT_NUMBER, service=service,timeout=5000, verbose=0, giveback=1))

    file=open("/users/pedro/desktop/testdel.txt","w")
    i=1
    for jack in jobdeflist:
        if i>1: file.write('\n')
        file.write(jack['jobId'])
        i+=1
    file.close











    file=open("/users/pedro/desktop/testdel.txt","r")
    jobdeflist=[]
    for x in file:
        x=x.replace("\n","")
        jobdeflist.append(x)
    file.close

    basepath="/Users/pedro/CTI/ID/MLab/NDT/BigQuery/Results/Tests/"

    for definition in jobdeflist:
        result=viewSyncQuery(projectId=PROJECT_NUMBER, jobId=definition, service=service, giveback=1, verbose=0)
        path=basepath+definition+'.txt'
        outputter(path,result)
    


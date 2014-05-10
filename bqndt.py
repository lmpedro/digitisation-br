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


def DefQlist(onedate=1, onequery=1):

    brcond='AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.country_name) AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.region) AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.city) AND connection_spec.client_geolocation.country_name="Brazil"'
    geovar= ', connection_spec.client_geolocation.region AS region, connection_spec.client_geolocation.city AS city, connection_spec.client_geolocation.latitude AS lat, connection_spec.client_geolocation.longitude AS lon'
    basicvars= ', test_id AS test_id, STRFTIME_UTC_USEC(UTC_USEC_TO_DAY(web100_log_entry.log_time * 1000000), "%Y-%m-%d") AS day'

    condition=[
               'IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.remote_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.local_ip)AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.HCThruOctetsAcked) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeRwin) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeCwnd) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeSnd) AND IS_EXPLICITLY_DEFINED(project) AND project = 0 AND IS_EXPLICITLY_DEFINED(connection_spec.data_direction) AND connection_spec.data_direction = 1 AND IS_EXPLICITLY_DEFINED(web100_log_entry.is_last_entry) AND web100_log_entry.is_last_entry = True AND web100_log_entry.snap.HCThruOctetsAcked >= 8192 AND (web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd) >= 9000000 AND (web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd) < 3600000000 AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.CongSignals) AND web100_log_entry.snap.CongSignals > 0 %s' % brcond,
               'IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.remote_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.local_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.HCThruOctetsReceived) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.Duration) AND IS_EXPLICITLY_DEFINED(project) AND project = 0 AND IS_EXPLICITLY_DEFINED(connection_spec.data_direction) AND connection_spec.data_direction = 0 AND IS_EXPLICITLY_DEFINED(web100_log_entry.is_last_entry) AND web100_log_entry.is_last_entry = True AND web100_log_entry.snap.HCThruOctetsReceived >= 8192 AND web100_log_entry.snap.Duration >= 9000000 AND web100_log_entry.snap.Duration < 3600000000 %s' % brcond,
               'IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.remote_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.local_ip)AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.HCThruOctetsAcked) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeRwin) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeCwnd) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeSnd) AND IS_EXPLICITLY_DEFINED(project) AND project = 0 AND IS_EXPLICITLY_DEFINED(connection_spec.data_direction) AND connection_spec.data_direction = 1 AND IS_EXPLICITLY_DEFINED(web100_log_entry.is_last_entry) AND web100_log_entry.is_last_entry = True AND web100_log_entry.snap.HCThruOctetsAcked >= 8192 AND (web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd) >= 9000000 AND (web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd) < 3600000000 AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.MinRTT) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.CountRTT) AND web100_log_entry.snap.CountRTT > 0 %s' % brcond,
               'IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.remote_ip) AND IS_EXPLICITLY_DEFINED(web100_log_entry.connection_spec.local_ip)AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.HCThruOctetsAcked) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeRwin) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeCwnd) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SndLimTimeSnd) AND IS_EXPLICITLY_DEFINED(project) AND project = 0 AND IS_EXPLICITLY_DEFINED(connection_spec.data_direction) AND connection_spec.data_direction = 1 AND IS_EXPLICITLY_DEFINED(web100_log_entry.is_last_entry) AND web100_log_entry.is_last_entry = True AND web100_log_entry.snap.HCThruOctetsAcked >= 8192 AND (web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd) >= 9000000 AND (web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd) < 3600000000 AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.SumRTT) AND IS_EXPLICITLY_DEFINED(web100_log_entry.snap.CountRTT) AND web100_log_entry.snap.CountRTT > 10 %s' % brcond,
               ]

    varselect=[
               'web100_log_entry.connection_spec.remote_ip AS ip_remote,            web100_log_entry.connection_spec.local_ip AS ip_local,            (web100_log_entry.snap.HCThruOctetsAcked/            (web100_log_entry.snap.SndLimTimeRwin +             web100_log_entry.snap.SndLimTimeCwnd +             web100_log_entry.snap.SndLimTimeSnd)) AS dspeed, (web100_log_entry.snap.SndLimTimeCwnd/            (web100_log_entry.snap.SndLimTimeRwin +             web100_log_entry.snap.SndLimTimeCwnd +             web100_log_entry.snap.SndLimTimeSnd)) AS netlimited, (web100_log_entry.snap.SndLimTimeCwnd/            (web100_log_entry.snap.SndLimTimeRwin +             web100_log_entry.snap.SndLimTimeCwnd +             web100_log_entry.snap.SndLimTimeSnd)) AS sndlimited %s %s ' % (geovar, basicvars),
               'web100_log_entry.connection_spec.remote_ip AS ip_remote,            web100_log_entry.connection_spec.local_ip AS ip_local, web100_log_entry.snap.HCThruOctetsReceived/web100_log_entry.snap.Duration AS uspeed %s' %geovar,
               'web100_log_entry.connection_spec.remote_ip AS ip_remote,            web100_log_entry.connection_spec.local_ip AS ip_local,            web100_log_entry.snap.MinRTT AS minrtt %s %s ' % (geovar, basicvars),
               'web100_log_entry.connection_spec.remote_ip AS ip_remote,            web100_log_entry.connection_spec.local_ip AS ip_local,            (web100_log_entry.snap.SumRTT/web100_log_entry.snap.CountRTT) AS avgrtt %s %s ' % (geovar, basicvars),
               ]

    if onedate:
        datelist=[]
        ano=2014
        i=4
        datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
    else:
        datelist=[]
        for ano in range(2009,2015):
            if ano==2009:
                for i in range(2,13):
                    datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
            elif ano==2014:
                for i in range(1,5):
                    datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))
            else:
                for i in range(1,13):
                    datelist.append('measurement-lab:m_lab.%i_%02i' %(ano, i))

    qlist=[]
    if onequery:
        for date in datelist:
            qlist.append('SELECT %s FROM [%s] WHERE %s' % (varselect[0], date, condition[0]))
    else:
        for x, y in zip(varselect, condition):
            for date in datelist:
                qlist.append('SELECT %s FROM [%s] WHERE %s' % (x, date, y))

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
def runSyncQuery (qdef, projectId, service, datasetId='', timeout=0,verbose=0,giveback=0):
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



def viewSyncQuery(projectId, jobId, service, datasetId='', timeout=0, verbose=1, giveback=0):
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


    print final
    print len(final)
    print len(final[0])
    print header

    for h in range(len(final)):
        for i in range(len(final[h])):
            if i>0: output.write(u"|")
            output.write(unicode(final[h][i]))
        output.write(u'\n')
    output.close()


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



qlist=DefQlist()

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
    result=viewSyncQuery(projectId=PROJECT_NUMBER, jobId=definition, service=service, giveback=1)
    path=basepath+definition+'.txt'
    outputter(path,result)



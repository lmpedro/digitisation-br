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


# Enter your Google Developer Project number
PROJECT_NUMBER = '448623832260'

FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/bigquery')



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

PROJECT_NUMBER = '448623832260'
service = servicer(PROJECT_NUMBER)
qdef=[
      "SELECT connection_spec.client_geolocation.city FROM [measurement-lab:m_lab.2014_03] WHERE connection_spec.client_geolocation.country_name='Brazil' AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.city) AND project=0 AND web100_log_entry.is_last_entry=1;",
      "SELECT COUNT(DISTINCT web100_log_entry.connection_spec.remote_ip) AS num_clients, connection_spec.client_geolocation.city AS city, AVG(web100_log_entry.snap.MinRTT) AS min, AVG(web100_log_entry.snap.CongSignals) as cong, FROM [measurement-lab:m_lab.2014_03] WHERE connection_spec.client_geolocation.country_name='Brazil' AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.city) AND project=0 AND web100_log_entry.is_last_entry=1 GROUP BY city ORDER BY num_clients;",
      "SELECT test_id AS test_id,  project AS project,  type AS type,  log_time AS log_time,  connection_spec.data_direction AS data_direction,  connection_spec.server_ip AS server_ip,  connection_spec.server_af AS server_af,  connection_spec.server_hostname AS server_hostname,  connection_spec.server_kernel_version AS server_kernel_version,  connection_spec.client_ip AS client_ip,  connection_spec.client_af AS client_af,  connection_spec.client_hostname AS client_hostname,  connection_spec.client_application AS client_application,  connection_spec.client_browser AS client_browser,  connection_spec.client_os AS client_os,  connection_spec.client_kernel_version AS client_kernel_version,  connection_spec.client_version AS client_version,  connection_spec.client_geolocation.continent_code AS client_continent_code,  connection_spec.client_geolocation.country_code AS client_country_code,  connection_spec.client_geolocation.country_code3 AS client_country_code3,  connection_spec.client_geolocation.country_name AS client_country_name,  connection_spec.client_geolocation.region AS client_region,  connection_spec.client_geolocation.metro_code AS client_metro_code,  connection_spec.client_geolocation.city AS client_city,  connection_spec.client_geolocation.area_code AS client_area_code,  connection_spec.client_geolocation.postal_code AS client_postal_code,  connection_spec.client_geolocation.latitude AS client_latitude,  connection_spec.client_geolocation.longitude AS client_longitude,  connection_spec.server_geolocation.continent_code AS server_continent_code,  connection_spec.server_geolocation.country_code AS server_country_code,  connection_spec.server_geolocation.country_code3 AS server_country_code3,  connection_spec.server_geolocation.country_name AS server_country_name,  connection_spec.server_geolocation.region AS server_region,  connection_spec.server_geolocation.metro_code AS server_metro_code,  connection_spec.server_geolocation.city AS server_city,  connection_spec.server_geolocation.area_code AS server_area_code,  connection_spec.server_geolocation.postal_code AS server_postal_code,  connection_spec.server_geolocation.latitude AS server_latitude,  connection_spec.server_geolocation.longitude AS server_longitude,  web100_log_entry.version AS w100version,  web100_log_entry.log_time AS w100log_time,  web100_log_entry.is_last_entry AS w100is_last_entry,  web100_log_entry.group_name AS w100group_name,  web100_log_entry.connection_spec.local_ip AS w100local_ip,  web100_log_entry.connection_spec.local_af AS w100local_af,  web100_log_entry.connection_spec.local_port AS w100local_port,  web100_log_entry.connection_spec.remote_ip AS w100remote_ip,  web100_log_entry.connection_spec.remote_port AS w100remote_port,  paris_traceroute_hop.protocol AS ptr_protocol,  paris_traceroute_hop.src_ip AS ptr_src_ip,  paris_traceroute_hop.src_af AS ptr_src_af,  paris_traceroute_hop.src_hostname AS ptr_src_hostname,  paris_traceroute_hop.dest_ip AS ptr_dest_ip,  paris_traceroute_hop.dest_af AS ptr_dest_af,  paris_traceroute_hop.dest_hostname AS ptr_dest_hostname,  paris_traceroute_hop.rtt AS ptr_rtt,  web100_log_entry.snap.LocalAddress AS w100_LocalAddress,  web100_log_entry.snap.LocalAddressType AS w100_LocalAddressType,  web100_log_entry.snap.LocalPort AS w100_LocalPort,  web100_log_entry.snap.RemAddress AS w100_RemAddress,  web100_log_entry.snap.RemPort AS w100_RemPort,  web100_log_entry.snap.WAD_IFQ AS w100_WAD_IFQ,  web100_log_entry.snap.WAD_MaxBurst AS w100_WAD_MaxBurst,  web100_log_entry.snap.WAD_MaxSsthresh AS w100_WAD_MaxSsthresh,  web100_log_entry.snap.WAD_NoAI AS w100_WAD_NoAI,  web100_log_entry.snap.WAD_CwndAdjust AS w100_WAD_CwndAdjust,  web100_log_entry.snap.ActiveOpen AS w100_ActiveOpen,  web100_log_entry.snap.MSSSent AS w100_MSSSent,  web100_log_entry.snap.MSSRcvd AS w100_MSSRcvd,  web100_log_entry.snap.WinScaleSent AS w100_WinScaleSent,  web100_log_entry.snap.WinScaleRcvd AS w100_WinScaleRcvd,  web100_log_entry.snap.SACK AS w100_SACK,  web100_log_entry.snap.TimeStamps AS w100_TimeStamps,  web100_log_entry.snap.ECN AS w100_ECN,  web100_log_entry.snap.SndWindScale AS w100_SndWindScale,  web100_log_entry.snap.RcvWindScale AS w100_RcvWindScale,  web100_log_entry.snap.WillSendSACK AS w100_WillSendSACK,  web100_log_entry.snap.WillUseSACK AS w100_WillUseSACK,  web100_log_entry.snap.TimeStampSent AS w100_TimeStampSent,  web100_log_entry.snap.TimeStampRcvd AS w100_TimeStampRcvd,  web100_log_entry.snap.SegsOut AS w100_SegsOut,  web100_log_entry.snap.DataSegsOut AS w100_DataSegsOut,  web100_log_entry.snap.DataOctetsOut AS w100_DataOctetsOut,  web100_log_entry.snap.HCDataOctetsOut AS w100_HCDataOctetsOut,  web100_log_entry.snap.SegsRetrans AS w100_SegsRetrans,  web100_log_entry.snap.OctetsRetrans AS w100_OctetsRetrans,  web100_log_entry.snap.SegsIn AS w100_SegsIn,  web100_log_entry.snap.DataSegsIn AS w100_DataSegsIn,  web100_log_entry.snap.DataOctetsIn AS w100_DataOctetsIn,  web100_log_entry.snap.HCDataOctetsIn AS w100_HCDataOctetsIn,  web100_log_entry.snap.Duration AS w100_Duration,  web100_log_entry.snap.ElapsedSecs AS w100_ElapsedSecs,  web100_log_entry.snap.ElapsedMicroSecs AS w100_ElapsedMicroSecs,  web100_log_entry.snap.StartTimeStamp AS w100_StartTimeStamp,  web100_log_entry.snap.CurMSS AS w100_CurMSS,  web100_log_entry.snap.PipeSize AS w100_PipeSize,  web100_log_entry.snap.MaxPipeSize AS w100_MaxPipeSize,  web100_log_entry.snap.SampleRTT AS w100_SampleRTT,  web100_log_entry.snap.SmoothedRTT AS w100_SmoothedRTT,  web100_log_entry.snap.RTTVar AS w100_RTTVar,  web100_log_entry.snap.MaxRTT AS w100_MaxRTT,  web100_log_entry.snap.MinRTT AS w100_MinRTT,  web100_log_entry.snap.SumRTT AS w100_SumRTT,  web100_log_entry.snap.HCSumRTT AS w100_HCSumRTT,  web100_log_entry.snap.CountRTT AS w100_CountRTT,  web100_log_entry.snap.CurRTO AS w100_CurRTO,  web100_log_entry.snap.MaxRTO AS w100_MaxRTO,  web100_log_entry.snap.MinRTO AS w100_MinRTO,  web100_log_entry.snap.SoftErrors AS w100_SoftErrors,  web100_log_entry.snap.SoftErrorReason AS w100_SoftErrorReason,  web100_log_entry.snap.IpTtl AS w100_IpTtl,  web100_log_entry.snap.IpTosIn AS w100_IpTosIn,  web100_log_entry.snap.IpTosOut AS w100_IpTosOut,  web100_log_entry.snap.SndUna AS w100_SndUna,  web100_log_entry.snap.SndNxt AS w100_SndNxt,  web100_log_entry.snap.SndMax AS w100_SndMax,  web100_log_entry.snap.ThruOctetsAcked AS w100_ThruOctetsAcked,  web100_log_entry.snap.HCThruOctetsAcked AS w100_HCThruOctetsAcked,  web100_log_entry.snap.RcvNxt AS w100_RcvNxt,  web100_log_entry.snap.ThruOctetsReceived AS w100_ThruOctetsReceived,  web100_log_entry.snap.HCThruOctetsReceived AS w100_HCThruOctetsReceived,  web100_log_entry.snap.SndLimTransRwin AS w100_SndLimTransRwin,  web100_log_entry.snap.SndLimTransCwnd AS w100_SndLimTransCwnd,  web100_log_entry.snap.SndLimTransSnd AS w100_SndLimTransSnd,  web100_log_entry.snap.SndLimTimeRwin AS w100_SndLimTimeRwin,  web100_log_entry.snap.SndLimTimeCwnd AS w100_SndLimTimeCwnd,  web100_log_entry.snap.SndLimTimeSnd AS w100_SndLimTimeSnd,  web100_log_entry.snap.SndLimBytesRwin AS w100_SndLimBytesRwin,  web100_log_entry.snap.SndLimBytesCwnd AS w100_SndLimBytesCwnd,  web100_log_entry.snap.SndLimBytesSender AS w100_SndLimBytesSender,  web100_log_entry.snap.State AS w100_State,  web100_log_entry.snap.Nagle AS w100_Nagle,  web100_log_entry.snap.SlowStart AS w100_SlowStart,  web100_log_entry.snap.CongAvoid AS w100_CongAvoid,  web100_log_entry.snap.CongSignals AS w100_CongSignals,  web100_log_entry.snap.OtherReductions AS w100_OtherReductions,  web100_log_entry.snap.X_OtherReductionsCM AS w100_X_OtherReductionsCM,  web100_log_entry.snap.X_OtherReductionsCV AS w100_X_OtherReductionsCV,  web100_log_entry.snap.CongOverCount AS w100_CongOverCount,  web100_log_entry.snap.CurCwnd AS w100_CurCwnd,  web100_log_entry.snap.MaxSsCwnd AS w100_MaxSsCwnd,  web100_log_entry.snap.MaxCaCwnd AS w100_MaxCaCwnd,  web100_log_entry.snap.LimCwnd AS w100_LimCwnd,  web100_log_entry.snap.CurSsthresh AS w100_CurSsthresh,  web100_log_entry.snap.MaxSsthresh AS w100_MaxSsthresh,  web100_log_entry.snap.MinSsthresh AS w100_MinSsthresh,  web100_log_entry.snap.LimSsthresh AS w100_LimSsthresh,  web100_log_entry.snap.InRecovery AS w100_InRecovery,  web100_log_entry.snap.FastRetran AS w100_FastRetran,  web100_log_entry.snap.Timeouts AS w100_Timeouts,  web100_log_entry.snap.SubsequentTimeouts AS w100_SubsequentTimeouts,  web100_log_entry.snap.CurTimeoutCount AS w100_CurTimeoutCount,  web100_log_entry.snap.AbruptTimeouts AS w100_AbruptTimeouts,  web100_log_entry.snap.DupAcksIn AS w100_DupAcksIn,  web100_log_entry.snap.SACKsRcvd AS w100_SACKsRcvd,  web100_log_entry.snap.SACKBlocksRcvd AS w100_SACKBlocksRcvd,  web100_log_entry.snap.PreCongSumCwnd AS w100_PreCongSumCwnd,  web100_log_entry.snap.PreCongSumRTT AS w100_PreCongSumRTT,  web100_log_entry.snap.PostCongSumRTT AS w100_PostCongSumRTT,  web100_log_entry.snap.PostCongCountRTT AS w100_PostCongCountRTT,  web100_log_entry.snap.ECNsignals AS w100_ECNsignals,  web100_log_entry.snap.SendStall AS w100_SendStall,  web100_log_entry.snap.QuenchRcvd AS w100_QuenchRcvd,  web100_log_entry.snap.RetranThresh AS w100_RetranThresh,  web100_log_entry.snap.NonRecovDAEpisodes AS w100_NonRecovDAEpisodes,  web100_log_entry.snap.SumOctetsReordered AS w100_SumOctetsReordered,  web100_log_entry.snap.NonRecovDA AS w100_NonRecovDA,  web100_log_entry.snap.SpuriousFrDetected AS w100_SpuriousFrDetected,  web100_log_entry.snap.SpuriousRtoDetected AS w100_SpuriousRtoDetected,  web100_log_entry.snap.DSACKDups AS w100_DSACKDups,  web100_log_entry.snap.MaxMSS AS w100_MaxMSS,  web100_log_entry.snap.MinMSS AS w100_MinMSS,  web100_log_entry.snap.SndInitial AS w100_SndInitial,  web100_log_entry.snap.RecInitial AS w100_RecInitial,  web100_log_entry.snap.CurRetxQueue AS w100_CurRetxQueue,  web100_log_entry.snap.MaxRetxQueue AS w100_MaxRetxQueue,  web100_log_entry.snap.CurAppWQueue AS w100_CurAppWQueue,  web100_log_entry.snap.MaxAppWQueue AS w100_MaxAppWQueue,  web100_log_entry.snap.X_Sndbuf AS w100_X_Sndbuf,  web100_log_entry.snap.CurRwinSent AS w100_CurRwinSent,  web100_log_entry.snap.MaxRwinSent AS w100_MaxRwinSent,  web100_log_entry.snap.MinRwinSent AS w100_MinRwinSent,  web100_log_entry.snap.ZeroRwinSent AS w100_ZeroRwinSent,  web100_log_entry.snap.LimRwin AS w100_LimRwin,  web100_log_entry.snap.LimMSS AS w100_LimMSS,  web100_log_entry.snap.DupAckEpisodes AS w100_DupAckEpisodes,  web100_log_entry.snap.RcvRTT AS w100_RcvRTT,  web100_log_entry.snap.DupAcksOut AS w100_DupAcksOut,  web100_log_entry.snap.CERcvd AS w100_CERcvd,  web100_log_entry.snap.ECESent AS w100_ECESent,  web100_log_entry.snap.ECNNonceRcvd AS w100_ECNNonceRcvd,  web100_log_entry.snap.CurReasmQueue AS w100_CurReasmQueue,  web100_log_entry.snap.MaxReasmQueue AS w100_MaxReasmQueue,  web100_log_entry.snap.CurAppRQueue AS w100_CurAppRQueue,  web100_log_entry.snap.MaxAppRQueue AS w100_MaxAppRQueue,  web100_log_entry.snap.X_Rcvbuf AS w100_X_Rcvbuf,  web100_log_entry.snap.X_wnd_clamp AS w100_X_wnd_clamp,  web100_log_entry.snap.X_rcv_ssthresh AS w100_X_rcv_ssthresh,  web100_log_entry.snap.X_dbg1 AS w100_X_dbg1,  web100_log_entry.snap.X_dbg2 AS w100_X_dbg2,  web100_log_entry.snap.X_dbg3 AS w100_X_dbg3,  web100_log_entry.snap.X_dbg4 AS w100_X_dbg4,  web100_log_entry.snap.CurRwinRcvd AS w100_CurRwinRcvd,  web100_log_entry.snap.MaxRwinRcvd AS w100_MaxRwinRcvd,  web100_log_entry.snap.MinRwinRcvd AS w100_MinRwinRcvd,  web100_log_entry.snap.ZeroRwinRcvd AS w100_ZeroRwinRcvd, FROM [measurement-lab:m_lab.2014_03] WHERE connection_spec.client_geolocation.country_name='Brazil' AND IS_EXPLICITLY_DEFINED(connection_spec.client_geolocation.city) AND project=0 AND web100_log_entry.is_last_entry=1;",
      ]
jobId='job_ouivGD0WVYFGCSUFRotpBILxoNc'
#jobReference=runSyncQuery(qdef=qdef[1],projectId=PROJECT_NUMBER, service=service,timeout=5000)

#data=viewSyncQuery(projectId=jobReference['projectId'], jobId=jobReference['jobId'], service=service, giveback=1)
#data=viewSyncQuery(projectId=PROJECT_NUMBER, jobId=jobId, service=service, giveback=1)

#outputter('/Users/pedro/desktop/aaa.txt',data)

a,b=runSyncQuery(qdef=qdef[1],projectId=PROJECT_NUMBER, service=service,timeout=5000, verbose=1, giveback=2)
print b
print a

'''
Results of NDT tests are indicated in BigQuery with
    project = 0
Results of client-to-server tests are indicated in BigQuery with
    connection_spec.data_direction = 0
Results of server-to-client tests are indicated in BigQuery with
    connection_spec.data_direction = 1
    
To estimate the performance of a user connection, NDT attempts to stress the connection, by creating congestion between the user’s machine and an M-Lab server. An NDT test can end in 3 possible states:
...
The test ends after the first congestion episode. In this case, the both peak values and averages in the test results are valid data points. This condition is expressed in BigQuery with:

    web100_log_entry.snap.CongSignals > 1

Test results extracted from the last line of every web100 log are indicated in BigQuery with
    web100_log_entry.is_last_entry = True

The duration of a server-to-client test is
    web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimTimeSnd

The duration of a client-to-server test is
    web100_log_entry.snap.Duration

The data transferred during of a client-to-server test is
    web100_log_entry.snap.HCThruOctetsReceived

The data transferred during of a server-to-client test is
    web100_log_entry.snap.HCThruOctetsAcked


complete?
For client-to-server tests:
web100_log_entry.snap.Duration >= 9000000
For server-to-client tests:
web100_log_entry.snap.SndLimTimeRwin + web100_log_entry.snap.SndLimTimeCwnd + web100_log_entry.snap.SndLimT
We also exclude results from tests that lasted much longer than expected (e.g., 10 min), because this is likely a symptom of problems during the test run.


'''
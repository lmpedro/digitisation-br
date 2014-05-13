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


varlist='test_id, project, log_time, connection_spec.server_ip, connection_spec.server_af, connection_spec.server_hostname, connection_spec.server_kernel_version, connection_spec.client_ip, connection_spec.client_af, connection_spec.client_hostname, connection_spec.client_os, connection_spec.client_kernel_version, connection_spec.client_version, connection_spec.client_browser, connection_spec.client_application, connection_spec.data_direction, connection_spec.client_geolocation.continent_code, connection_spec.client_geolocation.country_code, connection_spec.client_geolocation.country_code3, connection_spec.client_geolocation.country_name, connection_spec.client_geolocation.region, connection_spec.client_geolocation.metro_code, connection_spec.client_geolocation.city, connection_spec.client_geolocation.area_code, connection_spec.client_geolocation.postal_code, connection_spec.client_geolocation.latitude, connection_spec.client_geolocation.longitude, connection_spec.server_geolocation.continent_code, connection_spec.server_geolocation.country_code, connection_spec.server_geolocation.country_code3, connection_spec.server_geolocation.country_name, connection_spec.server_geolocation.region, connection_spec.server_geolocation.metro_code, connection_spec.server_geolocation.city, connection_spec.server_geolocation.area_code, connection_spec.server_geolocation.postal_code, connection_spec.server_geolocation.latitude, connection_spec.server_geolocation.longitude, type, web100_log_entry.version, web100_log_entry.log_time, web100_log_entry.group_name, web100_log_entry.connection_spec.remote_ip, web100_log_entry.connection_spec.remote_port, web100_log_entry.connection_spec.local_ip, web100_log_entry.connection_spec.local_af, web100_log_entry.connection_spec.local_port, web100_log_entry.snap.LocalAddress, web100_log_entry.snap.LocalAddressType, web100_log_entry.snap.LocalPort, web100_log_entry.snap.RemAddress, web100_log_entry.snap.RemPort, web100_log_entry.snap.WAD_IFQ, web100_log_entry.snap.WAD_MaxBurst, web100_log_entry.snap.WAD_MaxSsthresh, web100_log_entry.snap.WAD_NoAI, web100_log_entry.snap.WAD_CwndAdjust, web100_log_entry.snap.ActiveOpen, web100_log_entry.snap.MSSSent, web100_log_entry.snap.MSSRcvd, web100_log_entry.snap.WinScaleSent, web100_log_entry.snap.WinScaleRcvd, web100_log_entry.snap.SACK, web100_log_entry.snap.TimeStamps, web100_log_entry.snap.ECN, web100_log_entry.snap.SndWindScale, web100_log_entry.snap.RcvWindScale, web100_log_entry.snap.WillSendSACK, web100_log_entry.snap.WillUseSACK, web100_log_entry.snap.TimeStampSent, web100_log_entry.snap.TimeStampRcvd, web100_log_entry.snap.SegsOut, web100_log_entry.snap.DataSegsOut, web100_log_entry.snap.DataOctetsOut, web100_log_entry.snap.HCDataOctetsOut, web100_log_entry.snap.SegsRetrans, web100_log_entry.snap.OctetsRetrans, web100_log_entry.snap.SegsIn, web100_log_entry.snap.DataSegsIn, web100_log_entry.snap.DataOctetsIn, web100_log_entry.snap.HCDataOctetsIn, web100_log_entry.snap.Duration, web100_log_entry.snap.ElapsedSecs, web100_log_entry.snap.ElapsedMicroSecs, web100_log_entry.snap.StartTimeStamp, web100_log_entry.snap.CurMSS, web100_log_entry.snap.PipeSize, web100_log_entry.snap.MaxPipeSize, web100_log_entry.snap.SampleRTT, web100_log_entry.snap.SmoothedRTT, web100_log_entry.snap.RTTVar, web100_log_entry.snap.MaxRTT, web100_log_entry.snap.MinRTT, web100_log_entry.snap.SumRTT, web100_log_entry.snap.HCSumRTT, web100_log_entry.snap.CountRTT, web100_log_entry.snap.CurRTO, web100_log_entry.snap.MaxRTO, web100_log_entry.snap.MinRTO, web100_log_entry.snap.SoftErrors, web100_log_entry.snap.SoftErrorReason, web100_log_entry.snap.IpTtl, web100_log_entry.snap.IpTosIn, web100_log_entry.snap.IpTosOut, web100_log_entry.snap.SndUna, web100_log_entry.snap.SndNxt, web100_log_entry.snap.SndMax, web100_log_entry.snap.ThruOctetsAcked, web100_log_entry.snap.HCThruOctetsAcked, web100_log_entry.snap.RcvNxt, web100_log_entry.snap.ThruOctetsReceived, web100_log_entry.snap.HCThruOctetsReceived, web100_log_entry.snap.SndLimTransRwin, web100_log_entry.snap.SndLimTransCwnd, web100_log_entry.snap.SndLimTransSnd, web100_log_entry.snap.SndLimTimeRwin, web100_log_entry.snap.SndLimTimeCwnd, web100_log_entry.snap.SndLimTimeSnd, web100_log_entry.snap.SndLimBytesRwin, web100_log_entry.snap.SndLimBytesCwnd, web100_log_entry.snap.SndLimBytesSender, web100_log_entry.snap.State, web100_log_entry.snap.Nagle, web100_log_entry.snap.SlowStart, web100_log_entry.snap.CongAvoid, web100_log_entry.snap.CongSignals, web100_log_entry.snap.OtherReductions, web100_log_entry.snap.X_OtherReductionsCM, web100_log_entry.snap.X_OtherReductionsCV, web100_log_entry.snap.CongOverCount, web100_log_entry.snap.CurCwnd, web100_log_entry.snap.MaxSsCwnd, web100_log_entry.snap.MaxCaCwnd, web100_log_entry.snap.LimCwnd, web100_log_entry.snap.CurSsthresh, web100_log_entry.snap.MaxSsthresh, web100_log_entry.snap.MinSsthresh, web100_log_entry.snap.LimSsthresh, web100_log_entry.snap.InRecovery, web100_log_entry.snap.FastRetran, web100_log_entry.snap.Timeouts, web100_log_entry.snap.SubsequentTimeouts, web100_log_entry.snap.CurTimeoutCount, web100_log_entry.snap.AbruptTimeouts, web100_log_entry.snap.DupAcksIn, web100_log_entry.snap.SACKsRcvd, web100_log_entry.snap.SACKBlocksRcvd, web100_log_entry.snap.PreCongSumCwnd, web100_log_entry.snap.PreCongSumRTT, web100_log_entry.snap.PostCongSumRTT, web100_log_entry.snap.PostCongCountRTT, web100_log_entry.snap.ECNsignals, web100_log_entry.snap.SendStall, web100_log_entry.snap.QuenchRcvd, web100_log_entry.snap.RetranThresh, web100_log_entry.snap.NonRecovDAEpisodes, web100_log_entry.snap.SumOctetsReordered, web100_log_entry.snap.NonRecovDA, web100_log_entry.snap.SpuriousFrDetected, web100_log_entry.snap.SpuriousRtoDetected, web100_log_entry.snap.DSACKDups, web100_log_entry.snap.MaxMSS, web100_log_entry.snap.MinMSS, web100_log_entry.snap.SndInitial, web100_log_entry.snap.RecInitial, web100_log_entry.snap.CurRetxQueue, web100_log_entry.snap.MaxRetxQueue, web100_log_entry.snap.CurAppWQueue, web100_log_entry.snap.MaxAppWQueue, web100_log_entry.snap.X_Sndbuf, web100_log_entry.snap.CurRwinSent, web100_log_entry.snap.MaxRwinSent, web100_log_entry.snap.MinRwinSent, web100_log_entry.snap.ZeroRwinSent, web100_log_entry.snap.LimRwin, web100_log_entry.snap.LimMSS, web100_log_entry.snap.DupAckEpisodes, web100_log_entry.snap.RcvRTT, web100_log_entry.snap.DupAcksOut, web100_log_entry.snap.CERcvd, web100_log_entry.snap.ECESent, web100_log_entry.snap.ECNNonceRcvd, web100_log_entry.snap.CurReasmQueue, web100_log_entry.snap.MaxReasmQueue, web100_log_entry.snap.CurAppRQueue, web100_log_entry.snap.MaxAppRQueue, web100_log_entry.snap.X_Rcvbuf, web100_log_entry.snap.X_wnd_clamp, web100_log_entry.snap.X_rcv_ssthresh, web100_log_entry.snap.X_dbg1, web100_log_entry.snap.X_dbg2, web100_log_entry.snap.X_dbg3, web100_log_entry.snap.X_dbg4, web100_log_entry.snap.CurRwinRcvd, web100_log_entry.snap.MaxRwinRcvd, web100_log_entry.snap.MinRwinRcvd, web100_log_entry.snap.ZeroRwinRcvd, web100_log_entry.is_last_entry'
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
    qlist.append('SELECT %s FROM [%s] WHERE %s' %(varlist, date, condition))


destDatasetId='digitisationBR'
#destTableId='ndt_br'
PROJECT_NUMBER = '448623832260'





FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/bigquery')

service = servicer(PROJECT_NUMBER)


'''
#Deletes the final table, if it exists
#try: deleteTable(projectId='448623832260', service=service, datasetId=destDatasetId, tableId=destTableId)
#except:
    #print "Iargh!"
'''
#Creates the intermediary tables
'''
i=0
print 'Qlist length is: %i' % (len(qlist))
for qdef, date in zip(qlist, datelist):
    i+=1
    print i
    destTableId='ndtbr_'+date[-7:][:4]+date[-2:]
    check=getTable(projectId=PROJECT_NUMBER,service=service,datasetId=destDatasetId,tableId=destTableId)
    if check == None:
        runAsyncQuery(qdef=qdef, service=service, destDatasetId=destDatasetId, destTableId=destTableId, priority='BATCH', writeDisposition='WRITE_EMPTY')
        time.sleep(120)

'''
'''
#Creates the final table
qdef="SELECT * FROM (TABLE_QUERY(ndtexplorer:digitisationBR,'table_id CONTAINS \"ndtbr_\"'))"
destTableId='ndt_br'
runAsyncQuery(qdef=qdef, service=service, destDatasetId=destDatasetId, destTableId=destTableId, priority='BATCH', writeDisposition='WRITE_EMPTY', allowLargeResults=True)

'''
'''
#Deletes the intermediary tables created
i=0
for qdef, date in zip(qlist, datelist):
    i+=1
    print i
    destTableId='ndtbr'+date[-7:][:4]+date[-2:]
    deleteTable(service=service, projectId=PROJECT_NUMBER, datasetId=destDatasetId, tableId=destTableId)
    time.sleep(1)
'''

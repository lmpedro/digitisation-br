
'''
Order of the tests:
    dload, netlimited (congestion), sndlimited
    upload
    MinRTT
    AvgRTT
'''

for i in range(2009,2015,-1):
    print i

for i in reversed(range(2009,2015)):
    print i

joke= """
Select this
and that
and do this
"""

print joke

date='measurement-lab:m_lab.2014_04'

a='ndtbr'+date[-7:][:4]+date[-2:]
print a
print date[-7:][:4]

qdef="SELECT * FROM (TABLE_QUERY(ndtexplorer:digitisationBR,'table_id CONTAINS \"ndtbr\"'))"
print qdef
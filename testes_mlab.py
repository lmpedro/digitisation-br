import pprint
import subprocess
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
'''
i=1.11112323
print i
if i==int(i):
    print i
input = '/Users/pedro/CTI/ID/Statas/Escolas do PBLE_info.csv'
def schemaCreator(input):
    file=open(input,'r')
    helpingHand={}
    i=0
    for x in file:
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

hhh=schemaCreator(input)
pprint.pprint(hhh)

'''
input = '/Users/pedro/CTI/ID/Statas/Escolas do PBLE_info.csv'
filename=input.split('.')[-2]
subline='iconv -f macroman -t utf-8 \"%s\"' % (input)
converted=subprocess.check_output(subline,shell=True).split('\n')

print bbb



def schemaCreatorb(input):
    file=input
    helpingHand={}
    i=0
    for x in file:
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

hhh=schemaCreatorb(bbb)
pprint.pprint(hhh)


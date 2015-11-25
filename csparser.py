import urllib2
import hashlib
import re
import os.path
from bs4 import BeautifulSoup 

cache_dir="cache/"
data_dir="data/"

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def getHTML(process,year,phase,page):
        url="http://admision.unsa.edu.pe/admision/"+process+year+"f"+phase+"/"+page+".htm"
        hash_url=hashlib.md5(url).hexdigest()
        data_file_name=cache_dir+hash_url+".data"
        if(os.path.isfile(data_file_name)):
            with open(data_file_name,"r") as cache_file:
                response=cache_file.read()
        else:
            try:
                response=urllib2.urlopen(url).read()
                with open(data_file_name,"w") as cache_file:
                    cache_file.write(response)
            except urllib2.URLError, err:
                print "Error ("+process+year+phase+page+"):",err.reason
                return ""
        return response

def getMaxMin(process,year,phase):
    html=getHTML(process,year,phase,"maxmin")
    if not html:
        return []

    major=[]
    pmax=[]
    pmin=[]
    soup=BeautifulSoup(html)
    for field in soup.findAll('td',{'class':'lis-tabl'}):
        if field.text.startswith("Max"):
            pmax.append(float(re.findall("\d+.\d+",field.text)[0]))
        elif field.text.startswith("Min"):
                pmin.append(float(re.findall("\d+.\d+",field.text)[0]))
        elif field.text:
            major.append(field.text)

    data=[]
    for i in range(len(major)):
        data.append([major[i],pmax[i],pmin[i]])
    return data

def getPosVac(process,year,phase):
    dict_data={}
    pos=[]
    vac=[]

    htmlpos=getHTML(process,year,phase,"postulantes")
    if not htmlpos:
        return []

    major=[]
    soup=BeautifulSoup(htmlpos)
    for field in soup.findAll('td',{'class':'lis-tabl'}):
        if field.text.startswith("("):
            pos.append(int(re.findall("\d+",field.text)[0]))
        elif field.text and field.text[0].isalpha():
            major.append(field.text)

    for i in range(len(major)):
        if(not dict_data.has_key(major[i])):
            dict_data[major[i]]=[pos[i]]
        else:
            dict_data[major[i]].append(pos[i]) 

    htmlvac=getHTML(process,year,phase,"vacantes")
    if not htmlvac:
        return []

    major=[]
    soup=BeautifulSoup(htmlvac)
    for field in soup.findAll('td',{'class':'lis-tabl'}):
        if field.text.startswith("("):
            vac.append(int(re.findall("\d+",field.text)[0]))
        elif field.text and field.text[0].isalpha():
            major.append(field.text)

    for i in range(len(major)):
        if(not dict_data.has_key(major[i])):
            dict_data[major[i]]=[vac[i]]
        else:
            dict_data[major[i]].append(vac[i]) 

    data=[]
    for p,d in dict_data.iteritems():
        data.append([p,d[0],d[1]])
    return data

processes=["or","cpu"]
infos=["maxmin","posvac"]

def fillFullData(process,info):
    fullData={}
    for y in range(2010,2017):
        p=processes[process]
        for ph in range(1,4):
            if info==0:
                data=getMaxMin(p,str(y),str(ph))
            elif info==1:
                data=getPosVac(p,str(y),str(ph))

            label=str(y)+"-"+str(ph)
            if len(data)>1:
                for i in range(len(data)):
                    if(not fullData.has_key(data[i][0])):
                        fullData[data[i][0]]=[[label,[data[i][1],data[i][2]]]]
                    else:
                        fullData[data[i][0]].append([label,[data[i][1],data[i][2]]])
                print "("+label+") "+processes[process]+"-"+infos[info]+" OK"
            else:
                print "("+label+") "+processes[process]+"-"+infos[info]+" FAIL"
    return fullData

for process in range(2):
    for info in range(2):
        for c,v in fillFullData(process,info).iteritems():
            name=''.join(e for e in c if e.isalnum()).lower()
            file_name=name+"-"+processes[process]+"-"+infos[info]+".csv"
            with open(data_dir+file_name,"w") as fileCSV:
                for i in v:
                    fileCSV.write(i[0]+"\t")
                    for j in i[1]:
                        fileCSV.write(str(j)+"\t")
                    fileCSV.write("\n")

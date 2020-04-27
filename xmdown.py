#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#coding=utf-8

import time,random
import sys,os
import re,json,hashlib,string
import regex
import requests
import wget 

xmHeader = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'}

base_url = 'https://www.ximalaya.com'
base_api = 'https://www.ximalaya.com/revision/play/album?albumId={}&pageNum={}&sort=0&pageSize=30'
time_api = 'https://www.ximalaya.com/revision/time'
                
        

        
def getIndexPage(idxurl):
	#print idxurl
	idxhtml = requests.get(idxurl, headers=xmHeader)
	idxhtml.encoding = idxhtml.apparent_encoding
	#print idxhtml.text
	t = re.findall(r'<h1 class="title lO_">(.*?)</h1>', idxhtml.text)[0]
	#print t[0]
	i = re.findall(r'/(\d+)', idxurl)[0]
	return idxhtml, parseTitle(t), i
	
	
def checkM4aList(store_path):
    
    if os.path.exists('%s.m4alist' % store_path):
        return True
    else:
        return False	
	return 
	
	
def getSign():
	nowtime = str(int(time.time() * 1000))
	servertime = requests.get(time_api, headers=xmHeader).text
	
	str1 = str(hashlib.md5("himalaya-{}".format(servertime).encode()).hexdigest())
	str2 = "({})".format(str(int(round(random.random() * 100))))
	str3 = "({})".format(str(int(round(random.random() * 100))))
	sign =  str1+ str2 + servertime + str3 + nowtime
	xmHeader["xm-sign"] = sign.encode()
		
	return
	
#import unicodedata
#tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
#                      if unicodedata.category(unichr(i)).startswith('P'))
#def remove_punctuation(text):
#    return text.translate(tbl)
def parseTitle(t):
    out = "".join(t.split())
    out2 = out.replace('\t', '')
    out3 = re.sub('[\t\r()/|]', '', out2)
    out4 = regex.sub(ur"\p{P}+", "", out3)
    #out3 = re.sub(string.punctuation, '', out2)
    #out4 = re.sub('\W+', '', out3)
    return str(out4)
    
def getM4aList(epid, path, idxtext):
    
    m4alist=[]
    rs = re.findall(r'step="1" min="1" max="(\d+)"', idxtext)
    #print rs[0]
    if len(rs):
        pageCount = rs[0]
        
    else:
        pageCount = u'1'
	
    #print pageCount
	
    if pageCount:
		#print pageCount
        print u'专辑共 %d 页' % int(pageCount)
        for page in range(1, int(pageCount) + 1):
			print('解析第' + str(page) + '/{}页...'.format(pageCount))
			getSign()
			r = requests.get(base_api.format(epid, page), headers=xmHeader)
			r_json = json.loads(r.text)
			for audio in r_json['data']['tracksAudioPlay']:
				m4a={}
				audio_title = str(audio['trackName']).replace(' ', '')
				audio_src = str(audio['src'])
				m4a['url'] = audio_src
				#m4a['title'] = parseTitle(audio_title)
				m4a['title'] = (audio_title)
				m4alist.append(m4a)				
			# 每爬取1页，30个音频，休眠5秒
			time.sleep(5)
    else:
		print('未正常获得专辑页数')
		sys.exit()
    with open('%s.m4alist' % path,"w") as f:
		json.dump(m4alist, f)
		f.close()
    print u'共 %d 条音频条目' % len(m4alist)
    return

def get_detail(self, title, src, path):
	r_audio_src = self.s.get(src, headers=self.header)
	m4a_path = path + title + '.m4a'
	if not os.path.exists(m4a_path):
		with open(m4a_path, 'wb') as f:
			f.write(r_audio_src.content)
			print(title + '保存完毕...')
	else:
		print(title + 'm4a已存在')	

def getM4a(path):
#guess xm-sign not necessary
    with open('%s.m4alist' % path,'r') as f:
		m4alist = json.load(f)
    total=len(m4alist)
    i=0
	
    for s in m4alist:
        i+=1
        if len(s['url']) <= 8:
            #print 'bad addr: s%' % s['url']
            break
        if not os.path.exists( '%s%s.m4a' % (path, parseTitle(s['title']))):
            print u'\n(%d/%d)正在下载:\t%s' % (i, total,s['title'])
            wget.download(s['url'], out = '%s%s.m4a' % (path, parseTitle(s['title'])))
        else:
            print u'\n%s 已下载过' %   parseTitle(s['title'])
    return


def tes():
#guess xm-sign not necessary
    with open('/data/data/com.termux/files/home/prj/getxmly/神墓/大灰狼/.m4alist','r') as f:
		m4alist = json.load(f)
    print len(m4alist)
    
	
    for s in m4alist:
        print parseTitle(s['title'])
        
    return


if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	
	#tes()
	#sys.exit()
	
	
	if len(sys.argv) != 2:
		print u'用法: python ' + os.path.basename(sys.argv[0]) + ' http://www.ximalaya.com/youshengshu/1122334/'
		print u'程序以专辑名称作为目录名保存下载的文件\n\n'
		sys.exit()
	
	print u'\n\n------喜马拉雅音频批量下载------'
	
	print u'获取专辑首页信息...'
	idxhtml, title, epid = getIndexPage(sys.argv[1])
	print u'专辑名称（ID）：' + title +'（'+epid+'）'
	
	m4aPath = os.getcwd()+'/{}/'.format(title)
	print u'下载目录：' + m4aPath 
	if not os.path.exists(m4aPath):
		os.makedirs(m4aPath)
	
	if not checkM4aList(m4aPath):
		print u'生成文件下载列表...'
		getM4aList(epid, m4aPath, idxhtml.text)
	
	print u'文件下载列表已生成，开始下载...'
	getM4a(m4aPath)
	print u'\n\n------完成------'
	

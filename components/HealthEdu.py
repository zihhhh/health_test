import re
import requests
from linebot.models import *

class GetYoutubeLink():
    def __init__(self, n=1, lists = []):
        self._n = n
        self._lists = lists
        self._table = []
        self._urls=['https://www.youtube.com/c/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E8%A1%9B%E7%94%9F%E7%A6%8F%E5%88%A9%E9%83%A8/videos' # 中華民國衛生福利部
                    ,'https://www.youtube.com/user/taiwancdc/videos' # 衛生福利部疾病管制署
                    ,'https://www.youtube.com/user/hpagov/videos' # 衛生福利部國民健康署
                    ,'https://www.youtube.com/channel/UCVkryqwFXRc94ZThKMaXdIQ/videos'# 食藥好文網TFDA
                    ,'https://www.youtube.com/c/%E8%A1%9B%E7%94%9F%E7%A6%8F%E5%88%A9%E9%83%A8%E7%A4%BE%E6%9C%83%E5%8F%8A%E5%AE%B6%E5%BA%AD%E7%BD%B2/videos' # 衛生福利部社會及家庭署
                    ,'https://www.youtube.com/user/myegovnhi/videos' # 衛生福利部中央健康保險署
                    ,'https://www.youtube.com/channel/UCaHvaC68xsKWT2itI-0utJw/videos' # 衛生福利部【長照專區】
                    ]
    
    def youtubeLinks(self, url):
        r = requests.get(url)
        reg = re.compile('\/watch\?v\=\w+\-?\w?')
        num = 0
        for i in reg.findall(r.text):
            if num < self._n:
                link = 'http://www.youtube.com'
                if(len(i) == 20):
                    link+=i
                    self._table.append(link)
                    num+=1
                
    def getLinkLists(self):
        if len(self._lists) == 0:
            for i in self._urls:
                self.youtubeLinks(i)
        else:
            for tag in self._lists:
                i = self._urls[tag]
                self.youtubeLinks(i)
        return self._table

class GetNewsLink():
    def __init__(self):
        self._urls = ['https://www.hpa.gov.tw/Pages/TopicList.aspx?nodeid=4306'
                ,'https://www.hpa.gov.tw/Pages/TopicList.aspx?nodeid=127'
            ]
        self._t0=re.compile('\/Pages\/Detail\.aspx\?nodeid\=4306\&pid\=[0-9]{5}')
        self._t1=re.compile('\/Pages\/Detail\.aspx\?nodeid\=127\&pid\=[0-9]{5}')
        self._links=[]
        self._titles=[]
    def newsLinks(self, url, reg):
        r = requests.get(url)
        link = 'https://www.hpa.gov.tw'
        n = 0
        for item in reg.findall(r.text):
            if n >1:
                break
            temp=requests.get(link+item)
            title=''
            for i in range (30):
                ch=temp.text[temp.text.index('description')+22+i]
                if ch == '\"':
                    break
                title+=ch
            self._titles.append(title)
            self._links.append(link+item)
            n+=1
    def getLinkLists(self):
        self.newsLinks(self._urls[0], self._t0)
        self.newsLinks(self._urls[1], self._t1)
        return self._links, self._titles

class HealthMessage():
    def __init__(self):
        pass
    
    def showYoutube(self, youtubeLinks):
        message=[]
        for item in youtubeLinks:
            message.append(TextSendMessage(text=item))
        return message
    
    def showNews(self, links, titles):
        message = []
        for i in range(len(links)):
            message.append(TextSendMessage(text= titles[i]+'\n'+links[i]))
        return message

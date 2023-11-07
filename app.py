from __future__ import unicode_literals
from flask import Flask, request, abort

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction, MessageTemplateAction,
    PostbackAction, DatetimePickerAction, URITemplateAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton, ImagemapSendMessage, BaseSize,
    URIImagemapAction, ImagemapArea, MessageImagemapAction
)
import errno
import os
import sys
import tempfile
import requests
import json
import operator
from argparse import ArgumentParser
import datetime as dt
from datetime import datetime
import googletrans
import csv
import time, statistics
import BubbleMsg
import ImagemapMsg
import CarouselMsg
from LineInitializer import (channel_secret, channel_access_token, line_bot_api, handler)
from components.EatAdviceMessage import (EatAdviceMessage, EatAdvice)
from models.User import User
import config
import constant
import mysql.connector
import re
import requests
from bs4 import BeautifulSoup
import openai
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')
cnx = mysql.connector.connect(user='user_80956', password='m+c3zHYVaFBSz#w6', host='140.114.88.137', port='3306', database='mhealth_with_line')
cursor = cnx.cursor()

app = Flask(__name__)

# flag of language
lang = 0 # read from DB

# @TODO 想辦法解決 global status 影響到所有user的問題
status = 0
"""
0 for normal
1 for food recognition
2 for BP
3 for water
4 for temp
5 for food add
6 for sport add
7 for eating order
8 for weight
9 for height
10 for age
11 for sport select
12 for bodyFatRate,
13 for food add with customizeName and image
14 for change personal disease
15 for changemeal or weight
16 for authorization
17 for recommend path
18 for recommend meal
"""
imagePath = None
tmpData = None

disease = [0,0,0,0]

# the text of home
homeC = [' 您好!!', '您今天的運動進度: ', '您今天的飲食建議: ']
homeE = [' Hello!!', 'Today\'s process of exercise: ', 'Today\'s suggestions of diet: ']
home = [homeC, homeE]
# the text of food
foodC = ['請上傳食物的相片', '拍攝照片', '相簿上傳']
foodE = ['Please upload the photo of food', 'Take a photo', 'Upload from album']
food = [foodC, foodE]
# the text of body
bodyC = ['體重: ', '身高: ', '今日紀錄', '新增紀錄']
bodyE = ['Weight: ', 'Height: ', 'Today\'s record', 'New record']
body = [bodyC, bodyE]
# the text of bot
botC = ['飲食順序', '飲食建議', '一周圖表', '其他問題']
botE = ['Eating order', 'Eating suggestions', 'Weekly graph', 'Other questions']
bot = [botC, botE]
# the text of record
recordC = ['今日飲食', '今日運動', '詳細紀錄(至網站觀看)', '新增紀錄']
recordE = ['Today\'s diet', 'Today\'s exercise', 'More detail', 'New record']
record = [recordC, recordE]
# the text of diet
dietC = ['早餐', '午餐', '晚餐', '點心']
dietE = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
diet = [dietC, dietE]
#the text of exercise
exerciseC = ['強度緩和運動', '強度中等運動', '強度劇烈運動']
exerciseE = ['Light exercise', 'Moderate exercise', 'Drastic exercise']
exercise = [exerciseC, exerciseE]
#the text of setting
setC = ['語言', '更改個人資訊', '關於智慧e聊健康']
setE = ['Language', 'Basic information', 'Specific diseases', 'About Health Chat']
sett = [setC, setE]
#the text of habit
dA = 'A. 大部分時間都坐著'
dB = 'B. 坐著工作但有時會走動'
dC = 'C. 大部分時間都站著或走動'
dD = 'D. 勞力負荷工作'
rA = 'A. 大部分坐著'
rB = 'B. 多為三十分內的走動'
rC = 'C. 規律運動且超過三十分'
rD = 'D. 每次超過一小時劇烈運動'

# the model of clarifai , [0] for TW , [1] for EN
# (Deprecated)
# clarifai_appC = ClarifaiApp(api_key='dbdc72277b1f44d2afe37421d0971698')
# clarifai_modelC = clarifai_appC.public_models.food_model
# clarifai_appE = ClarifaiApp(api_key='f4568827dad44f71a7309759419a8bbe')
# clarifai_modelE = clarifai_appE.public_models.food_model
# clarifai_model = [clarifai_modelC, clarifai_modelE]

# Clarifai gRPC client
stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
# This is how you authenticate.
# metadataC = (('authorization', 'Key dbdc72277b1f44d2afe37421d0971698'),)
# metadataE = (('authorization', 'Key f4568827dad44f71a7309759419a8bbe'),)
metadataC = (('authorization', f'Key aa3dea7f885445768b04c73a88781005'),)
metadataE = (('authorization', f'Key aa3dea7f885445768b04c73a88781005'),)

# List of collaborated beacon HWID
hwID_list = ['0125f93bd3', '0126846195']

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

import utility
from MessageRouter import MessageRouter
from controllers.EatAdviceController import EatAdviceController
from controllers.SearchController import SearchController
from controllers.EatIntroduceController import EatIntroduceController
from controllers.GroupController import GroupController
from controllers.DietRecordController import DietRecordController
from controllers.HealthReminder import HealthReminder

textRouter = MessageRouter('text')
textRouter.add('飲食建議', EatAdviceController.replyAdviceMessage)
# textRouter.add('.*吃.*|.*喝.*', EatAdviceController.askForFood)
textRouter.add('群組目標', GroupController.groupTarget)
textRouter.add('.*天.*|.*日.*|.*吃.*', DietRecordController.askDietRecord)

textRouter.add('.*開.*運動.*', HealthReminder.sportReminder)
textRouter.add('.*開.*熱量.*', HealthReminder.calorieReminder)

postbackRouter = MessageRouter('postback')

postbackRouter.add('/ketogenicDiet', EatIntroduceController.ketogenicDiet)
postbackRouter.add('/ketoA', EatIntroduceController.ketoA)
postbackRouter.add('/ketoB', EatIntroduceController.ketoB)
postbackRouter.add('/ketoC', EatIntroduceController.ketoC)
postbackRouter.add('/muscleDiet', EatIntroduceController.muscleDiet)
postbackRouter.add('/muscleA', EatIntroduceController.muscleA)
postbackRouter.add('/muscleB', EatIntroduceController.muscleB)
postbackRouter.add('/muscleC', EatIntroduceController.muscleC)
postbackRouter.add('/dashDiet', EatIntroduceController.dashDiet)
postbackRouter.add('/dashA', EatIntroduceController.dashA)
postbackRouter.add('/dashB', EatIntroduceController.dashB)
postbackRouter.add('/dashC', EatIntroduceController.dashC)
postbackRouter.add('/glutenfreeDiet', EatIntroduceController.glutenfreeDiet)
postbackRouter.add('/glutenA', EatIntroduceController.glutenA)
postbackRouter.add('/glutenB', EatIntroduceController.glutenB)
postbackRouter.add('/glutenC', EatIntroduceController.glutenC)

postbackRouter.add('/caloriegraph', SearchController.caloriegraph)
postbackRouter.add('/dietgraph', SearchController.dietgraph)
postbackRouter.add('/sportgraph', SearchController.sportgraph)
postbackRouter.add('/watergraph', SearchController.watergraph)
postbackRouter.add('/pressuregraph', SearchController.pressuregraph)
postbackRouter.add('/tempgraph', SearchController.temperaturegraph)

postbackRouter.add('/today_diet', SearchController.searchDietToday)
postbackRouter.add('/today_sport', SearchController.searchSportToday)
postbackRouter.add('/today_BP', SearchController.searchBloodPressureToday)
postbackRouter.add('/today_water', SearchController.searchWaterToday)
postbackRouter.add('/today_temp', SearchController.searchTempToday)

postbackRouter.add('/keep_health', HealthReminder.keepHealth)
postbackRouter.add('/lose_weight', HealthReminder.loseWeight)

postbackRouter.add('/health_record_overview', SearchController.recordOverview)
postbackRouter.add('/query_record_botton', SearchController.bubbleMsg)

from components.BeaconMessage import BeaconMessage
from components.HealthEdu import HealthMessage, GetNewsLink
import CompanyMessage
beaconMessage = BeaconMessage()
healthMessage = HealthMessage()

import threading
import time

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


# 注意 !
# 自動推播(月上限500)測試時別帶上

# CompanyMessage.PushMessage(line_bot_api) // first
# set_interval(job1,86400*2) // period

# one day = 86400 sec

# 注意 !
# 自動推播(月上限500)測試時別帶上

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/notification", methods=['POST'])
def push_notification():

    to = request.json['to']
    text = request.json['messages'][0]['text']

    #line_bot_api.push_message(to, TextSendMessage(text=text))
    CompanyMessage.PushMessage(line_bot_api, to, text)

    return 'OK'

@app.route("/rankings",methods=['POST'])
def get_data():

    lineIDList = request.json['lineIDList']
    category = request.json['category']

    for i in range(len(lineIDList)):

        query = "INSERT INTO `rankings`(`lineID`,`category`,`dataVariation`) VALUES (%s, %s, %s)"
        cursor.execute(query, (lineIDList[i], category, request.json['currentData'][i] - request.json['previousData'][i]))
        cnx.commit()

    return 'OK'




@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    global lang, status, imagePath, tmpData
    
    #===========check whether user is in database==============
    
    profile = line_bot_api.get_profile(event.source.user_id)
    if (User.isUserIDExist(profile.user_id) == False):
        User.add(profile.user_id, profile.display_name)

    #====================end of checking=========================

    #If system makes user upload photo of food and users send another text ,then status should be 0.
    #Once the text is '/food', status will be set as 1 below ( text == '/food' )
    #status = 0

    if textRouter.route(event):
        return

    if text == '新增紀錄': #新增紀錄
        line_bot_api.reply_message(event.reply_token, ImagemapMsg.newRecord())
    elif text == 'id':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(event.source.user_id))
    #新功能
    elif text =="身體健康狀況諮詢":
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text='請輸入您的身體狀況')
        ])    
        status = 20
    elif text =="飲食順序建議":
            line_bot_api.reply_message(event.reply_token, [
                TextSendMessage(text='請輸入您欲食用的食物名稱')
            ])    
            status = 21
    elif text =="運動計畫規劃":
            line_bot_api.reply_message(event.reply_token, [
                TextSendMessage(text='請輸入您的目標或想從事的運動種類，如：一周消耗3000卡、跑步')
            ])    
            status = 22        
    elif text=="空氣品質查詢":
        message = TextSendMessage(
                text='點選定位並分享位置訊息以獲取空氣品質資訊',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=LocationAction(label="定位"))
                        ]
            ))
        line_bot_api.reply_message(event.reply_token,message)        
    

    elif text == '查詢紀錄': #查訊紀錄
        buttons_template = ButtonsTemplate(title='查詢紀錄', text='query record', actions=[
            PostbackAction(label='健康紀錄總覽', data='/health_record_overview'),
            PostbackAction(label='各項紀錄查詢', data='/query_record_botton')
        ])
        template_message = TemplateSendMessage(alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    
    elif text == '飲食順序':
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text='根據相關研究表明，高GI的食物愈後吃愈能控制血糖的上升\n\n'+
            '理想的飲食順序為:\n1. 蔬菜類\n2. 蛋豆魚肉類\n3. 脂肪類\n4. 五穀根莖類\n5. 水果\n6. 飲料和甜點'),
            TextSendMessage(text='請輸入想吃的食物名稱\nex:牛排 沙拉 奶茶 巧克力蛋糕')
        ])
        status = 7
    elif text == '健康管家':
        data = { 'userID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)

        data = {'lineID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/disease/queryUserDisease.php', data = data)
        userDiseaseList = json.loads(response.text)
        
        message = FlexSendMessage(alt_text="healthInfo", contents=CarouselMsg.healthInfo(resultList, userDiseaseList))
        line_bot_api.reply_message(event.reply_token, message)
    elif text == 'advice':
        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlLogo, title='飲食建議',text='Eating suggestion',
            actions=[PostbackAction(label='生酮飲食',data='/ketogenicDiet'), PostbackAction(label='健身',data='/muscleDiet'),
                    PostbackAction(label='得舒飲食',data='/dashDiet'), PostbackAction(label='無麩質飲食',data='/glutenfreeDiet')])
        template_message = TemplateSendMessage(alt_text='Buttons alt text', template=buttons_template)
        diabete = '因為您患有糖尿病，所以甜食和醣類食物請盡量少吃，可多吃洋蔥、苦瓜、鱔魚等食物，有助血糖的控制'
        heart = '因為您患有心臟病，所以油炸食物、肥肉、動物內臟請盡量少吃，可多吃菠菜、魚類、黃豆類、堅果類等食物，能降低血脂和膽固醇，減少心臟病發作機率'
        highpressure = '因為您患有高血壓，所以肉類、濃茶(或咖啡)、酒、辛辣和重鹹食物請盡量少吃，可多吃豆類、綠色葉菜類(如芹菜)、魚類等食物，這些食物富含鉀、鎂等礦物質，能幫助降低血壓'
        belly = '因為您患有下腹突出，所以檸檬、柑橘、草莓、生食等食物請盡量少吃，避免一次攝取過多水分，可多吃祛寒食物，如辣椒、薑、咖哩、胡蘿蔔等，並且少量多餐'
        suggest = []
        
        if disease[0] == 1:
            suggest.append(TextSendMessage(text=diabete))
        if disease[1] == 1:
            suggest.append(TextSendMessage(text=heart))
        if disease[2] == 1:
            suggest.append(TextSendMessage(text=highpressure))
        if disease[3] == 1:
            suggest.append(TextSendMessage(text=belly))
        if len(suggest) == 0:
            suggest.append(TextSendMessage(text='您目前沒患有相關疾病，請繼續保持，注意脂肪、鹽、糖的攝取量'))
        
        suggest.append(template_message)        
        line_bot_api.reply_message(event.reply_token, suggest)
    elif text == '設定': #設定
        buttons_template = ButtonsTemplate(title='設定', text='settings', actions=[
            PostbackAction(label=sett[lang][0], data='/language'),
            PostbackAction(label=sett[lang][1], data='/info'),
            PostbackAction(label=sett[lang][2], data='/about')
        ])
        template_message = TemplateSendMessage(alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == '新增血壓':
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text='請輸入收縮壓(mmHg)/舒張壓(mmHg)/脈搏(times/min)，範例如下:\n120/80/70'),
            TextSendMessage(text='若取消請輸入N')
        ])
        status = 2
    elif text == '新增飲水':
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text='請輸入飲水量(ml)\nex: 100'),
            TextSendMessage(text='若取消請輸入N')
        ])
        status = 3
    elif text == '新增體溫':
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text='請輸入體溫(℃)\nex: 36.5'),
            TextSendMessage(text='若取消請輸入N')
        ])
        status = 4
    elif text == '新增運動':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入運動名稱及總時間(分鐘)，ex:\n\n棒球\n120'))
        status = 6
    elif text == '授權':
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url='https://i.imgur.com/ydGuUkA.png', 
                                                                        preview_image_url='https://i.imgur.com/ydGuUkA.png'))
        status = 16
    elif text == '取得授權':
        line_bot_api.reply_message(event.reply_token, 
            TemplateSendMessage(
                alt_text='開啟QRCode掃描器?',
                template=ConfirmTemplate(
                    text='開啟QRCode掃描器?',
                    actions=[
                        URIAction(
                            label='開啟',
                            uri=config.QR_CODE_SCANNER_LIFF_URI
                        ),
                        MessageAction(
                            label='取消',
                            text='no'
                        )
                    ]
                )
            ))
    elif text == '路線':
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = '請輸入預定運動路線長度(公尺):\n範例:1000'),
                                                    TextSendMessage(text = '若取消請輸入N')])
        status = 17
    elif text == '附近餐點推薦':
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text = '請輸入最低熱量需求(kcal):\n範例:1000'),
                                                    TextSendMessage(text = '若取消請輸入N')])
        status = 18
    elif text == 'beacon': # 測試beacon功能
        data = {
            'updateInfo' : 'nearBeacon',
            'userID' : event.source.user_id,
            'nearBeacon' : '0000000001'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        data = {
            'userID' : event.source.user_id,
            'kcal' : 10
        }
        response = requests.post(config.PHP_SERVER+'mhealth/Shop/RecommendShop.php', data = data)
        recommendList = json.loads(response.text)
        print(recommendList)

        message = [TextSendMessage(text= '附近餐點推薦'),
            FlexSendMessage(alt_text = '餐點推薦', contents = beaconMessage.nearbyFood(recommendList['arr_recommend'][0]))]
        line_bot_api.reply_message(event.reply_token, message)
    elif text == '衛教新知':
        getLinks = GetNewsLink()
        links, titles = getLinks.getLinkLists()
        message = healthMessage.showNews(links, titles)
        line_bot_api.reply_message(event.reply_token, message)
    elif text == '排行榜':

        #userId = request.json['events'][0]['source']['userId']

        query = "select rankings.lineID,lineUser.name,rankings.dataVariation from rankings,lineUser WHERE rankings.lineID = lineUser.lineID AND category = 'exerciseDuration' ORDER BY dataVariation DESC;"
        cursor.execute(query)
        results = cursor.fetchall()
        cnx.commit()

        lineIDList = []
        sortedData = []

        for i in range(len(results)):
            lineIDList.append(results[i][0])
            sortedData.append(int(results[i][2]))

        result = json.loads(json.dumps({
            "category": "exerciseDuration",
            "lineIDList": [lineIDList],
            "sortedData": sortedData
        }))

        message = FlexSendMessage(alt_text = 'health rank', contents = CompanyMessage.HealthRank(event.source.user_id, result))
        line_bot_api.reply_message(event.reply_token, message)
    elif text == '設定目標':
        buttons_template = ButtonsTemplate(title='健康提醒', text='setting reminder', actions=[
            PostbackAction(label='保持健康', data='/keep_health'),
            PostbackAction(label='減重', data='/lose_weight')
        ])
        template_message = TemplateSendMessage(alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == '視訊問診':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='視訊問診\nhttps://140.114.88.137:81/videocall.html'))

    elif text == '健康新知':
        print("hello")
        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已取消'))
        url = 'https://www.hpa.gov.tw/Home/Index.aspx'
        response = requests.get(url) 
        soup = BeautifulSoup(response.text, 'lxml')
        info_items = soup.find_all('div','newsList newsBlock')
        print("hello2")
        list_link=[]
        list_title=[]
        list_date=[]
        contents=dict()
        contents['type']='carousel'
        bubbles=[]
        print("hello2")
        for d in info_items:
            link = d.a['href']
            link="https://www.hpa.gov.tw"+link
            list_link.append(link)
            
            title = d.a['title']
            list_title.append(title)
            
            date=d.find('span','dateStyle')
            date=date.text
            list_date.append(date)

        for x in range(0,3):     
            bubble = BubbleContainer(
                                direction='ltr', 
                                body=BoxComponent(  
                                    layout='vertical',
                                    contents=[
                                        TextComponent(text=list_title[x] , weight='bold', size='xl',align='center',wrap=True,maxLines=2),
                                        
                                        BoxComponent(
                                            layout='vertical',
                                            margin='lg',
                                            contents=[
                                                BoxComponent(
                                                    layout='baseline',
                                                    contents=[
                                                        TextComponent(text=list_date[x], color='#aaaaaa', size='md', align='end',flex=2),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        BoxComponent(  
                                            layout='horizontal',
                                    margin='md',
                                    contents=[
                                        ButtonComponent(
                                            style='primary',
                                            height='sm',
                                            color='#003060',
                                            action=URIAction(label='看更多', uri=list_link[x]),
                                        )
                                                
                                            ]
                                        )
                                    ],
                                ),
                                
                            )
            bubbles.append(bubble)
        contents['contents']=bubbles
        message =FlexSendMessage(alt_text="new", contents=contents)
        line_bot_api.reply_message(event.reply_token,message)        
        
    elif text == '取消':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已取消'))
        status = 0
    elif text == '/home': #主頁
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text=profile.display_name + home[lang][0]),
                    TextSendMessage(text=home[lang][1] + '請繼續努力!!'),
                    TextSendMessage(text=home[lang][2] + '請少吃油炸食物喔!!'),
                    TextSendMessage(text='若想了解如何操作本帳號，請輸入/help'),
                    TextSendMessage(text='也歡迎進入我們的網站，了解更完整的功能\n'+ config.PHP_SERVER +'mhealth_web')
                ]
            )
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == '/help': #幫助
        line_bot_api.reply_message(event.reply_token,[
            TextSendMessage(text='請點選下方選單執行功能'),
            TextSendMessage(text='食物辨識可以藉由上傳食物的照片來自動幫您記錄每天的飲食'),
            TextSendMessage(text='生理資訊紀錄可以記錄身體相關資訊，幫助您做進一步的管理和提醒'),
            TextSendMessage(text='查看飲食與運動紀錄來檢視您每天的作息'),
            TextSendMessage(text='若是第一次使用我們，請先設定您的資訊喔\n\n1. 設定->基本資訊\n2. 設定->特殊疾病\n')
        ])
    elif text == 'N':
        if not status == 0:
            status = 0
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已取消'))
    else:
        if status == 2: # blood pressure
            if not len(text.split('/')) == 3:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            sbp = text.split('/')[0] # systolic
            dbp = text.split('/')[1] # diastolic
            pulse = text.split('/')[2]
            
            if isNum(sbp) and isNum(dbp) and isNum(pulse):
                buttons_template = ButtonsTemplate(title='選擇時間',text='time',actions=[
                    DatetimePickerAction(label='日期時間',data=text,mode='datetime'),
                    PostbackAction(label='取消',data='/cancel')
                ])
                template_message = TemplateSendMessage(alt_text='Button alt text',template=buttons_template)
                line_bot_api.reply_message(event.reply_token, template_message)
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
        #新功能
        elif status == 20:    
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="努力運轉中，請稍後 🥸"))
            print("使用chat gpt")
            messages = [
                #賦予人設
                {'role': 'system', 'content': '你現在是一位醫生，請給予以下身體狀況建議，限200字以內'}, 
    
                #提出問題
                {'role': 'user','content': event.message.text}
                ]
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            #max_tokens=128,
            temperature=0.5,
            messages=messages)
            content = response['choices'][0]['message']['content']
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content.strip()))
        elif status == 21:    
            print("使用chat gpt")
            messages = [
                #賦予人設
                {'role': 'system', 'content': '你是一位營養師，請給予以下食物食用順序的建議，限200字以內'}, 
    
                #提出問題
                {'role': 'user','content': event.message.text}
                ]
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            #max_tokens=128,
            temperature=0.5,
            messages=messages)
            content = response['choices'][0]['message']['content']
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content.strip()))

        elif status == 22:    
            print("使用chat gpt")
            messages = [
                #賦予人設
                {'role': 'system', 'content': '請設計一份300字以內的運動計畫且依據以下條件：'}, 
    
                #提出問題
                {'role': 'user','content': event.message.text}
                ]
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            #max_tokens=128,
            temperature=0.5,
            messages=messages)
            content = response['choices'][0]['message']['content']
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=content.strip()))    
        
        elif status == 3: # water intake
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                buttons_template = ButtonsTemplate(title='選擇時間',text='time',actions=[
                        DatetimePickerAction(label='日期時間',data=text,mode='datetime'),
                        PostbackAction(label='取消',data='/cancel')
                ])
                template_message = TemplateSendMessage(alt_text='Button alt text',template=buttons_template)
                line_bot_api.reply_message(event.reply_token, template_message)
        elif status == 4: # temperature
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                buttons_template = ButtonsTemplate(title='選擇時間',text='time',actions=[
                        DatetimePickerAction(label='日期時間',data=text,mode='datetime'),
                        PostbackAction(label='取消',data='/cancel')
                ])
                template_message = TemplateSendMessage(alt_text='Button alt text',template=buttons_template)
                line_bot_api.reply_message(event.reply_token, template_message)
        elif status == 6: # new exercise record
            if not len(text.split('\n')) == 2:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            inputName = text.split('\n')[0]
            inputTime = text.split('\n')[1]
            if not isNum(inputTime):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='時間格式錯誤，請重新輸入'))
            param = {
                'query': 'query',
                'name': inputName
            }
            response = requests.post(config.PHP_SERVER+'mhealth/sport/querySport.php', data=param)
            resultList = json.loads(response.text)
            print(resultList) # 符合名稱
            resultLen = len(resultList)
            columns = []
            actionList = []
            colMax = 5 #最多只有5個column

            while resultLen > 0 and colMax > 0: #建立column
                name = resultList.pop(0)
                if len(actionList) < 3:
                    if(len(name) > 19):
                        actionList.append(PostbackAction(label=(name[:15]+"..."), data=name+'@'+inputTime))
                    else:
                        actionList.append(PostbackAction(label=name, data=name+'@'+inputTime))
                else:
                    carouselColumn = CarouselColumn(text='sport',title='運動種類', actions=actionList)
                    columns.append(carouselColumn)
                    colMax = colMax - 1
                    actionList = []
                    if(len(name) > 19):
                        actionList.append(PostbackAction(label=(name[:15]+"..."), data=name+'@'+inputTime))
                    else:
                        actionList.append(PostbackAction(label=name, data=name+'@'+inputTime))
                resultLen = resultLen - 1
        
            if len(actionList) > 0 and colMax > 0: #有剩餘的空間(每個column有3個選項)
                while len(actionList) < 3:
                    actionList.append(PostbackAction(label='無',data='/None'))
                carouselColumn = CarouselColumn(text='sport',title='運動種類', actions=actionList)
                columns.append(carouselColumn)
                actionList = []

            if len(columns) == 0: #無紀錄(column=0)
                buttons_template = ButtonsTemplate(title='無相關運動種類',text='No result', actions=[
                    MessageTemplateAction(label='重新輸入', text='新增運動'),
                    PostbackAction(label='取消',data='/cancel')
                ])
                template_message1 = TemplateSendMessage(alt_text='category no found', template=buttons_template)
                line_bot_api.reply_message(event.reply_token, [template_message1])
            else:
                carousel_template = CarouselTemplate(columns=columns)
                confirm_template = ConfirmTemplate(text='重新輸入運動名稱或取消', actions=[
                    MessageTemplateAction(label='重新輸入', text='新增運動'),
                    PostbackAction(label='取消',data='/cancel')
                ])
                template_message1 = TemplateSendMessage(alt_text='相關運動', template=carousel_template)
                template_message2 = TemplateSendMessage(alt_text='運動記錄確認', template=confirm_template)
                line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(text='以下是我們搜尋到的相關運動，若沒有您滿意的請重行輸入或取消'),
                    template_message1,template_message2
                ])
            status = 11
        elif status == 7:
            foods = text.split(' ')
            # conflicts = requests.get("https://mhealth-service.feveral.me/api/food/conflict", params={"foods":foods}, verify=False).json()['conflicts']
            # print(foods)
            conflicts = utility.foodConflict(foods)
            # print(conflicts)
            answer = utility.order(text)
            messages = []
            lst = []
            for a in answer:
                lst.append(a[0])
            messages.append(TextSendMessage(text='建議您依照以下順序食用\n' + ' '.join(lst)))
            # print(utility.foodsMessage(conflicts))
            if len(conflicts) != 0:
                messages.append(TextSendMessage(text='餐點中含有食物相剋:'+ utility.foodsMessage(conflicts)))
            
            data = {'lineID' : event.source.user_id}
            response = requests.post(config.PHP_SERVER+'mhealth/disease/queryUserDisease.php', data = data)
            userDiseaseList = json.loads(response.text)

            DiseaseList = ['糖尿病', '心臟病', '高血壓', '下腹突出']
            for i in range(4):
                for item in userDiseaseList:
                    if DiseaseList[i] == item['disease']:
                        disease[i] = 1

            suggestions = ''
            for i in range(len(disease)):
                if disease[i] == 1:
                    diseaseMsg = utility.diseaseFood(foods, i, 'DiseaseFood.csv')
                    medicineMsg = utility.diseaseFood(foods, i, 'MedicineConflictList.csv')
                    print(medicineMsg)
                    if len(diseaseMsg) != 0 or len(medicineMsg) != 0:
                        suggestions = suggestions + '\n' + utility.suggestMessage(diseaseMsg, medicineMsg, i)
            if len(suggestions) != 0:
                messages.append(TextSendMessage(text = '因為您患有' + suggestions))

            line_bot_api.reply_message(event.reply_token, messages)
        elif status == 8: #更改體重
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                data = {
                    'updateInfo' : 'weight',
                    'userID' : event.source.user_id,
                    'weight' : text
                }
                response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
                data = {
                'recordInfo': 'weight',
                'userID': event.source.user_id,
                'water': text,
                'recordTime': datetime.now()
            }
                response = requests.post(config.PHP_SERVER+'mhealth/info/recordInfo.php', data = data)
                print(response)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='體重更新成功'))
                status = 0
        elif status == 9: #更改身高
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                data = {
                    'updateInfo' : 'height',
                    'userID' : event.source.user_id,
                    'height' : text
                }
                response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='身高更新成功'))
                status = 0
        elif status == 10: #更改年紀
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                data = {
                    'updateInfo' : 'age',
                    'userID' : event.source.user_id,
                    'age' : text
                }
                response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='年齡更新成功'))
                status = 0
        elif status == 12: #更改體脂率
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                data = {
                    'updateInfo' : 'bodyFatRate',
                    'userID' : event.source.user_id,
                    'bodyFatRate' : text
                }
                response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='體脂率更新成功'))
                status = 0
        elif status == 17: #路線
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                
                data = {
                    'userID' : event.source.user_id,
                    'target_len' : text # user 的輸入
                }
                response = requests.post(config.PHP_SERVER+'mhealth/SportPath/Path.php', data = data)
                recommendPath = json.loads(response.text)
                #print(recommendPath)
                message = FlexSendMessage(alt_text = '推薦路線', contents = beaconMessage.showPath(recommendPath))
                line_bot_api.reply_message(event.reply_token, message)
                status = 0
        elif status == 18: #附近餐點推薦
            if not isNum(text):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='格式錯誤，請重新輸入'))
            else:
                data = {
                    'userID' : event.source.user_id,
                    'kcal' : text
                }
                response = requests.post(config.PHP_SERVER+'mhealth/Shop/RecommendShop.php', data = data)
                recommendList = json.loads(response.text)
                print(recommendList)

                message = FlexSendMessage(alt_text = '餐點推薦', contents = beaconMessage.showList(recommendList['arr_recommend'][0]))
                line_bot_api.reply_message(event.reply_token, message)
                status = 0
        else:
            pass
'''
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )
'''

# 空氣品質函式
@handler.add(MessageEvent, message=LocationMessage)
def aqi(event):
    if isinstance(event.message, LocationMessage):
        global status
        address=event.message.address.replace('台','臺')
        print(address)
        city_list, site_list ={}, {}
        msg='找不到空氣品質資訊。'
        try:
            # 2022/12 時氣象局有修改了 API 內容，將部份大小寫混合全改成小寫，因此程式碼也跟著修正
            url = 'https://data.epa.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON'
            a_data = requests.get(url)             # 使用 get 方法透過空氣品質指標 API 取得內容
            a_data_json = a_data.json()            # json 格式化訊息內容
            for i in a_data_json['records']:       # 依序取出 records 內容的每個項目
                city = i['county']                 # 取出縣市名稱
                if city not in city_list:
                    city_list[city]=[]             # 以縣市名稱為 key，準備存入串列資料
                site = i['sitename']               # 取出鄉鎮區域名稱
                aqi = int(i['aqi'])                # 取得 AQI 數值
                status = i['status']               # 取得空氣品質狀態
                site_list[site] = {'aqi':aqi, 'status':status}  # 記錄鄉鎮區域空氣品質
                city_list[city].append(aqi)        # 將各個縣市裡的鄉鎮區域空氣 aqi 數值，以串列方式放入縣市名稱的變數裡
            for i in city_list:
                if i in address: # 如果地址裡包含縣市名稱的 key，就直接使用對應的內容
                    # 參考 https://airtw.epa.gov.tw/cht/Information/Standard/AirQualityIndicator.aspx
                    aqi_val = round(statistics.mean(city_list[i]),0)  # 計算平均數值，如果找不到鄉鎮區域，就使用縣市的平均值
                    aqi_status = ''  # 手動判斷對應的空氣品質說明文字
                    if aqi_val<=50: aqi_status = '良好'
                    elif aqi_val>50 and aqi_val<=100: aqi_status = '普通'
                    elif aqi_val>100 and aqi_val<=150: aqi_status = '對敏感族群不健康'
                    elif aqi_val>150 and aqi_val<=200: aqi_status = '對所有族群不健康'
                    elif aqi_val>200 and aqi_val<=300: aqi_status = '非常不健康'
                    else: aqi_status = '危害'
                    msg='空氣品質：'+str(aqi_status) +'  AQI：'+str(aqi_val)
                    break
            for i in site_list:
                if i in address:  # 如果地址裡包含鄉鎮區域名稱的 key，就直接使用對應的內容
                    msg=='空氣品質：'+str(site_list[i]["status"])+'  AQI：'+ str(site_list[i]["aqi"])
                    break
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))    
        except:
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    # Whether this message is image or not
    if isinstance(event.message, ImageMessage):
        global status
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)

        # Write image into a temporary file
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)

        # Change temporary file path with new one.
        tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        # Upload image to mhealth-server        
        url = 'https://selab1.cs.nthu.edu.tw/api/image?ext='+ext
        files = [('file', open(dist_path, 'rb'))]
        print("files: ", files)
        res = requests.post(url, files=files, verify=False)
        print("image upload",res.status_code)
        print(res.json().get('url'))

        # Liff
        imageLiffURI=config.ADD_FOOD_CAMERA_LIFF_URI+'?image='+res.json().get('url')[-36::1]
        print('liff compose:'+imageLiffURI)

        # Image path inside Heroku server
        imageUrl='https://health-checker-python.herokuapp.com/'+os.path.join('static', 'tmp', dist_name)
        print('imageURL (heroku): ', imageUrl)
        concept_request = service_pb2.PostModelOutputsRequest(
            # This is the model ID of a publicly available Food model.
            model_id='bd367be194cf45149e75f01d59f77ba7',
            inputs=[
                resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(url=imageUrl)))
        ])
        
        print('send concept request')
        response = stub.PostModelOutputs(concept_request, metadata=metadataE)
        print('concept model response: ', response)

        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " + str(response.status.code))
        # for concept in response.outputs[0].data.concepts:
        #     # print('%12s: %.2f' % (concept.name, concept.value))
        concepts = response.outputs[0].data.concepts
        print("辨識結果： ", concepts[0].name, ', ', concepts[1].name, ', ', concepts[2].name)
        foodRecognitionURI=imageLiffURI+'&food1='+concepts[0].name+'&food2='+concepts[1].name+'&food3='+concepts[2].name

        translator = googletrans.Translator()
        transTW = [
            translator.translate(concepts[0].name, dest = 'zh-tw').text,
            translator.translate(concepts[1].name, dest = 'zh-tw').text,
            translator.translate(concepts[2].name, dest = 'zh-tw').text
        ]
        
        # with open('tranlateList.csv', newline='') as csvfile:
        #     # 讀取 CSV 檔案內容
        #     rows = csv.reader(csvfile)
        #     # 以迴圈輸出每一列  
        #     print(print("beer: "), translator.translate('beer', dest='zh-tw').text)
        #     transTW = [
        #         translator.translate('beer', dest='zh-tw', src='en'),
        #         translator.translate(concepts[1].name,dest='zh-TW',src='en').text,
        #         translator.translate(concepts[2].name,dest='zh-TW',src='en').text
        #     ]
        
        #     for row in rows:
        #         for i in range(0,3):
        #             if concepts[i].name in row:
        #                 transTW[i] = row[1]
        #                 break
        
        print("辨識結果中文："+transTW[0]+','+transTW[1]+','+transTW[2])
        foodRecognitionURI=imageLiffURI+'&food1='+transTW[0]+'&food2='+transTW[1]+'&food3='+transTW[2]
        # print(transTW)
        conflicts = utility.foodConflict(transTW)
        # print(conflicts)
        messages = []
        buttons_template = TemplateSendMessage(
        alt_text='Buttons Template',
        template=ButtonsTemplate(
            title='食物辨識完成',
            text='點擊下方連結以進一步新增飲食',
            thumbnail_image_url=res.json().get('url'),
            actions=[
                URITemplateAction(
                    label='辨識結果',
                    uri=foodRecognitionURI
                    )
                ]
            )
        )
        messages.append(buttons_template)
        if len(conflicts) != 0:
            messages.append(TextSendMessage(text='餐點中含有食物相剋:'+ utility.foodsMessage(conflicts)))

        data = {'lineID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/disease/queryUserDisease.php', data = data)
        userDiseaseList = json.loads(response.text)

        DiseaseList = ['糖尿病', '心臟病', '高血壓', '下腹突出']
        for i in range(4):
            for item in userDiseaseList:
                if DiseaseList[i] == item['disease']:
                    disease[i] = 1

        suggestions = ''
        for i in range(len(disease)):
            if disease[i] == 1:
                diseaseMsg = utility.diseaseFood(transTW, i, 'DiseaseFood.csv')
                medicineMsg = utility.diseaseFood(transTW, i, 'MedicineConflictList.csv')
                print(medicineMsg)
                if len(diseaseMsg) != 0 or len(medicineMsg) != 0:
                    suggestions = suggestions + '\n' + utility.suggestMessage(diseaseMsg, medicineMsg, i)
        if len(suggestions) != 0:
            messages.append(TextSendMessage(text = '因為您患有' + suggestions))

        line_bot_api.reply_message(event.reply_token, messages)
    else:
        return  

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    pass

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    global lang, status, imagePath, disease, tmpData

    #===========check whether user is in database==============

    profile = line_bot_api.get_profile(event.source.user_id)
    if (User.isUserIDExist(profile.user_id) == False):
        User.add(profile.user_id, profile.display_name)

    #====================end of checking=========================  

    if postbackRouter.route(event):
        return

    elif event.postback.data == '/breakfast': #早餐查詢
        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'meal': '早餐',
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data=param)
        resultList = json.loads(response.text)
        message = FlexSendMessage(alt_text="today_breakfast", contents=BubbleMsg.todayDiet('早餐', resultList))
        line_bot_api.reply_message(event.reply_token, message)
    elif event.postback.data == '/lunch': #午餐查詢
        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'meal': '午餐',
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data=param)
        resultList = json.loads(response.text)
        message = FlexSendMessage(alt_text="today_lunch", contents=BubbleMsg.todayDiet('午餐', resultList))
        line_bot_api.reply_message(event.reply_token, message)
    elif event.postback.data == '/dinner': #晚餐查詢
        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'meal': '晚餐',
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data=param)
        resultList = json.loads(response.text)
        message = FlexSendMessage(alt_text="today_dinner", contents=BubbleMsg.todayDiet('晚餐', resultList))
        line_bot_api.reply_message(event.reply_token, message)
    elif event.postback.data == '/snack': #點心查詢
        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'meal': '點心',
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data=param)
        resultList = json.loads(response.text)
        message = FlexSendMessage(alt_text="today_snack", contents=BubbleMsg.todayDiet('點心', resultList))
        line_bot_api.reply_message(event.reply_token, message)      
    elif event.postback.data == '/language': #語言
        confirm_template = ConfirmTemplate(text='切換語言(Language Switch)', actions=[
            PostbackAction(label='中文', data='/chinese'),
            PostbackAction(label='英文', data='/english'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif event.postback.data == '/chinese': #中文
        data = {
            'updateInfo' : 'language',
            'userID' : event.source.user_id,
            'language' : 0
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        lang = 0
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='切換至中文'))
    elif event.postback.data == '/english': #英文
        data = {
            'updateInfo' : 'language',
            'userID' : event.source.user_id,
            'language' : 1
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        lang = 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Switch to English'))
    
    elif event.postback.data == '/info': #基本資訊
        data = {
            'userID': profile.user_id
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)
        userGender = ''
        userEatingHabit = ''
        if resultList['gender']=='male':
            userGender = '男'
        elif resultList['gender']=='female':
            userGender = '女'
        if resultList['eatingHabit'] == 'meat':
            userEatingHabit = '葷食'
        elif resultList['eatingHabit'] == 'vagetarian':
            userEatingHabit = '素食'
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(thumbnail_image_url=constant.imageUrlLogo, 
                title=profile.display_name, text='BMI: '+str(round(float(resultList['weight'])/((float(resultList['height'])/100)**2),1)), actions=[
                PostbackAction(label='體重: '+resultList['weight']+' kg', data='/weight'),
                PostbackAction(label='身高: '+resultList['height']+' cm', data='/height'),
                PostbackAction(label='年齡: '+resultList['age']+' 歲', data='/age')
            ]),
            CarouselColumn(thumbnail_image_url=constant.imageUrlLogo, 
                title='修改個人資訊', text='User information', actions=[
                PostbackAction(label='性別: '+userGender, data='/gender'),
                PostbackAction(label='飲食習慣: '+userEatingHabit, data='/eatingHabit'),
                PostbackAction(label='體脂率: '+str(resultList['bodyFatRate'])+' %', data='/bodyFatRate')
            ]),
            CarouselColumn(thumbnail_image_url=constant.imageUrlLogo, 
                title='修改個人資訊', text='User information', actions=[
                PostbackAction(label='工作量', data='/workLoad'),
                PostbackAction(label='疾病', data='/changeDisease'),
                PostbackAction(label='期望改善身體目標', data='/goal')
            ])
        ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif event.postback.data == '/weight': #體重
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text='請輸入新的體重(kg)，若取消請輸入N'))
        status = 8

    elif event.postback.data == '/height': #身高
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text='請輸入新的身高(cm)，若取消請輸入N'))
        status = 9
    elif event.postback.data == '/age': #年齡
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text='請輸入新的年齡，若取消請輸入N'))
        status = 10
    elif event.postback.data == '/gender': #性別
        confirm_template = ConfirmTemplate(text='選擇性別(Choose Gender)', actions=[
            PostbackAction(label='男 Male', data='/chooseMale'),
            PostbackAction(label='女 Female', data='/chooseFemale'),
        ])
        template_message = TemplateSendMessage(alt_text='Choose gender button',template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif event.postback.data == '/chooseMale':
        data = {
            'updateInfo' : 'gender',
            'userID' : event.source.user_id,
            'gender' : 'male'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='性別更新成功'))
    elif event.postback.data == '/chooseFemale':
        data = {
            'updateInfo' : 'gender',
            'userID' : event.source.user_id,
            'gender' : 'female'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='性別更新成功'))
    elif event.postback.data == '/eatingHabit': #飲食習慣
        confirm_template = ConfirmTemplate(text='選擇飲食習慣(Choose Eating Habit)', actions=[
            PostbackAction(label='葷食 Meat', data='/chooseMeat'),
            PostbackAction(label='素食 Vegetarian', data='/chooseVagetarian'),
        ])
        template_message = TemplateSendMessage(alt_text='Choose eating habit button',template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif event.postback.data == '/chooseMeat':
        data = {
            'updateInfo' : 'eatingHabit',
            'userID' : event.source.user_id,
            'eatingHabit' : 'meat'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='飲食習慣更新成功'))
    elif event.postback.data == '/chooseVagetarian':
        data = {
            'updateInfo' : 'eatingHabit',
            'userID' : event.source.user_id,
            'eatingHabit' : 'vagetarian'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='飲食習慣更新成功'))
    elif event.postback.data == '/bodyFatRate': #體脂率
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入新的體脂率，若取消請輸入N'))
        status = 12
    elif event.postback.data == '/workLoad':
        data = {
            'userID' : event.source.user_id
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)
        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlBurn, 
                text='目前狀態: '+resultList['workLoad'], title='工作量', actions=[
                PostbackAction(label= '臥床躺著不動', data='/workLoadA'),
                PostbackAction(label= '輕度(坐著居多)', data='/workLoadB'),
                PostbackAction(label= '中度(需站立或活動較多)', data='/workLoadC'),
                PostbackAction(label= '重度(如運動員)', data='/workLoadD')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif event.postback.data == '/workLoadA':
        data = {
            'updateInfo' : 'workLoad',
            'userID' : event.source.user_id,
            'workLoad' : '臥床躺著不動'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='工作量更新成功'))
    elif event.postback.data == '/workLoadB':
        data = {
            'updateInfo' : 'workLoad',
            'userID' : event.source.user_id,
            'workLoad' : '輕度工作者'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='工作量更新成功'))
    elif event.postback.data == '/workLoadC':
        data = {
            'updateInfo' : 'workLoad',
            'userID' : event.source.user_id,
            'workLoad' : '中度工作者'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='工作量更新成功'))
    elif event.postback.data == '/workLoadD':
        data = {
            'updateInfo' : 'workLoad',
            'userID' : event.source.user_id,
            'workLoad' : '重度工作者'
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='工作量更新成功'))
    elif event.postback.data == '/changeDisease':
        data = {
            'lineID' : event.source.user_id,
        }
        response = requests.post(config.PHP_SERVER+'mhealth/disease/queryUserDisease.php', data = data)
        if response.text:
            resultList = json.loads(response.text)
        else:
            resultList = dict
        message = FlexSendMessage(alt_text="healthInfo", contents=CarouselMsg.changeDisease(resultList))
        line_bot_api.reply_message(event.reply_token, message)
        status = 14
    elif event.postback.data == '/about':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='台灣的肥胖率在亞洲名列前茅，我們是來自清大資工系的學生，希望利用自身所學，幫助社會大眾為自身的健康把關'))
    elif event.postback.data == '/cancel':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已取消'))
        status = 0
    elif event.postback.data == '/None':
        pass
    elif event.postback.data[:12] == '/sportrecord': #將運動記錄到DB
        if status == 11:
            sportName = event.postback.data[12:].split("@")[0]
            sportTime = event.postback.data[12:].split("@")[1]
            print("success sport record")
            print(sportName)
            print(sportTime)
            param = {
                'queryName': 'queryName',
                'name': sportName,
            }
            response = requests.post(config.PHP_SERVER+'mhealth/sport/querySport.php', data=param)
            resultList = json.loads(response.text)
            print(resultList) # carolie/每kg美30min
            data = {
                'userID': profile.user_id
            }
            response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
            resultList2 = json.loads(response.text)
            weight = int(resultList2['weight'])
            # 總carolie = carolie/kg/30min * 重量 * 分鐘/30
            data = {
                'record': 'record',
                'userID': event.source.user_id,
                'name': sportName,
                'carolie': float(resultList[0])*weight*(int(sportTime)/30.0), # 乘以體重
                'totalTime': int(sportTime),
                'recordTime': datetime.now()
            }
            print(data)
            response = requests.post(config.PHP_SERVER+'mhealth/sport/recordSport.php', data=data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='新增運動記錄成功'))
            status = 0
    elif event.postback.data[:7] == '/mealID':
        mealID = event.postback.data[8:]
        query = """select mealID,mealName,calorie,carbohydrate,sugars,protein,fat,satFat,transFat,sodium,size from mealRecord where mealID = %s;"""
        cursor.execute(query, (mealID,))
        mealID_content = cursor.fetchone()
        cnx.commit()

        content_format = f"{mealID_content[1]}\n"+\
                         f"熱量:{mealID_content[2]:>24}大卡\n"+\
                         f"蛋白質:{mealID_content[5]:>22}公克\n"+\
                         f"脂肪:{mealID_content[6]:>25}公克\n"+\
                         f"  飽和脂肪:{mealID_content[7]:>18}公克\n"+\
                         f"  反式脂肪:{mealID_content[8]:>18}公克\n"+\
                         f"碳水化合物: {mealID_content[3]:>12}公克\n"+\
                         f"  糖:{mealID_content[4]:>29}公克\n"+\
                         f"鈉:{mealID_content[9]:>28}豪克"

        '''
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=mealID_content[1]+'\n'+
                                                                        '熱量:\t'+ str(mealID_content[2]) +'大卡\n'+
                                                                        '蛋白質:\t' + str(mealID_content[5]) + '公克\n' +
                                                                        '脂肪:\t' + str(mealID_content[6]) + '公克\n' +
                                                                        '  飽和脂肪:\t' + str(mealID_content[7]) + '公克\n' +
                                                                        '  反式脂肪:\t' + str(mealID_content[8]) + '公克\n'+
                                                                        '碳水化合物:\t'+ str(mealID_content[3]) +'公克\n'+
                                                                        '  糖:\t' + str(mealID_content[4]) + '公克\n' +
                                                                        '鈉:\t' + str(mealID_content[9]+'豪克')
                                                                        ))
        '''
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=content_format))


    else:
        print("postback status:",status)
        if status == 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Recieved'))
        elif status == 2: # blood pressure
            sbp = event.postback.data.split('/')[0] # systolic
            dbp = event.postback.data.split('/')[1] # diastolic
            pulse = event.postback.data.split('/')[2] # diastolic
            time = event.postback.params['datetime'] # time
            data = {
                'recordInfo': 'pulse',
                'userID': event.source.user_id,
                'sbp': sbp,
                'dbp': dbp,
                'pulse': pulse,
                'recordTime': time
            }
            response = requests.post(config.PHP_SERVER+'mhealth/info/recordInfo.php', data = data)
            print(response.text)
            ttt= str("收縮壓："+sbp+"舒張壓："+dbp+"脈搏"+pulse)
            
           
            
            print(ttt)
            print("使用chat gpt")
            messages = [
                #賦予人設
                {'role': 'system', 'content': '你現在是一位醫生，請給予以下身體狀況建議，限200字以內'}, 
    
                #提出問題
                {'role': 'user','content': ttt}
                ]
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
                #max_tokens=128,
            temperature=0.5,
            messages=messages)
            content = response['choices'][0]['message']['content']
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='新增血壓記錄成功。'+content.strip()))
            #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='新增血壓記錄成功'))
            

            status = 0
        elif status == 3: # water intake
            water = event.postback.data # water
            time = event.postback.params['datetime'] # time
            data = {
                'recordInfo': 'water',
                'userID': event.source.user_id,
                'water': water,
                'recordTime': time
            }
            response = requests.post(config.PHP_SERVER+'mhealth/info/recordInfo.php', data = data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='新增飲水記錄成功'))
            status = 0
        elif status == 4: # temperature
            temperature = event.postback.data # temperature
            time = event.postback.params['datetime'] # time
            data = {
                'recordInfo': 'temperature',
                'userID': event.source.user_id,
                'temperature': temperature,
                'recordTime': time
            }
            response = requests.post(config.PHP_SERVER+'mhealth/info/recordInfo.php', data = data)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='新增體溫記錄成功'))
            status = 0
        elif status == 11:
            print(event.postback.data) # 從資料庫選取的運動名稱
            name = event.postback.data.split("@")[0]
            time = event.postback.data.split("@")[1]
            param = {
                'queryName': 'queryName',
                'name': name,
            }
            response = requests.post(config.PHP_SERVER+'mhealth/sport/querySport.php', data=param)
            resultList = json.loads(response.text)
            print(resultList)
            print('query sport name')
            buttons_template = ButtonsTemplate(title='新增運動紀錄',text=name, actions=[PostbackAction(label='時間: '+time+'分鐘', data='/None')])
            template_message = TemplateSendMessage(alt_text='運動資訊', template=buttons_template)
            confirm_template = ConfirmTemplate(text='確認或取消',actions=[
                    PostbackAction(label='確認',data='/sportrecord'+name+"@"+time),
                    PostbackAction(label='取消',data='/cancel')])
            template_message2 = TemplateSendMessage(alt_text='新增記錄確認', template=confirm_template)
            line_bot_api.reply_message(event.reply_token, [template_message,template_message2])
        elif status == 14:
            diseaseName = event.postback.data.split("@")[1]
            if diseaseName == 'cancel':
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已取消'))
            else:
                param = {
                    'lineID': event.source.user_id,
                }
                response = requests.post(config.PHP_SERVER+'mhealth/disease/queryUserDisease.php', data=param)
                resultList = json.loads(response.text)
                isExist = False
                for row in resultList:
                    if row['disease'] == diseaseName:
                        isExist = True
                        break
                if isExist:
                    param = {
                        'lineID': event.source.user_id,
                        'disease': diseaseName,
                    }
                    response = requests.post(config.PHP_SERVER+'mhealth/disease/deleteUserDisease.php', data=param) 
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已刪除'+diseaseName))
                else:
                    param = {
                        'lineID': event.source.user_id,
                        'disease': diseaseName,
                    }
                    response = requests.post(config.PHP_SERVER+'mhealth/disease/insertUserDisease.php', data=param) 
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已新增'+diseaseName))
            status = 0


@handler.add(BeaconEvent)
def handle_beacon(event):

    if event.beacon.type == 'enter':
        data = {
            'updateInfo' : 'nearBeacon',
            'userID' : event.source.user_id,
            'nearBeacon' : event.beacon.hwid
        }
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/updateUserInfo.php', data = data)
        # update user`s nearest beacon
        '''
        data = {
            'userID' : event.source.user_id,
            'kcal' : 10
        }
        response = requests.post(config.PHP_SERVER+'mhealth/Shop/RecommendShop.php', data = data)
        recommendList = json.loads(response.text)
        message = [TextSendMessage(text= '附近餐點推薦'),
            FlexSendMessage(alt_text = '餐點推薦', contents = beaconMessage.nearbyFood(recommendList['arr_recommend'][0]))]
        line_bot_api.reply_message(event.reply_token, message)
        '''


        query = """SELECT 10000*weight/(height*height) AS bmi,age,IF(gender='male',1,2) FROM lineUser WHERE `lineID` = %s"""
        cursor.execute(query, (event.source.user_id,))
        userData = cursor.fetchone()
        userData_dict = {"bmi": userData[0], "age": userData[1], "gender": userData[2]}
        cnx.commit()

        query2 = """SELECT type,plainText,filter,it FROM broadcastMessageInfo WHERE `hwid` = %s ORDER BY it ASC"""
        #query2 = """select i.messageId,i.hwid,b.mode,i.plainText,i.filter from broadcastMessageInfo as i,broadcastInfo as b where i.hwid = b.hwid and i.hwid = %s;"""
        cursor.execute(query2, (event.beacon.hwid,))
        broadcastMessageList = cursor.fetchall()
        cnx.commit()

        query3 = """SELECT mode FROM broadcastInfo where `hwid` = %s"""
        cursor.execute(query3, (event.beacon.hwid,))
        broadcast_mode = cursor.fetchone()
        cnx.commit()



        userBroadcastMessage = []
        host_url = 'https://selab1.cs.nthu.edu.tw/mhealth/'

        if(broadcast_mode[0]=="restaurant"):
            #print("restaurant")
            query4 = """select m.mealID,mealName,calorie,carbohydrate,sugars,protein,fat,satFat,transFat,sodium,size,description,imagePath,targetAge,IF(targetGender='male',1,2),PushMessage,IsPush from mealRecord m, (select s.targetAge,s.targetGender,s.mealID,s.PushMessage,s.IsPush from broadcastInfo b,shopTarget s where `hwid` = %s and b.shopID=s.shopID) c where m.mealID = c.mealID;"""
            cursor.execute(query4,(event.beacon.hwid,))
            mealBroadcastInfo = cursor.fetchall()
            cnx.commit()

            for i in mealBroadcastInfo:
                flag = False
                if userData_dict["age"] == i[13]:
                    flag = True
                if userData_dict["gender"] == i[14]:
                    flag = True

                if flag:
                    userBroadcastMessage.append(
                        CarouselColumn(
                            thumbnail_image_url=host_url+i[12],
                            title=i[1],
                            text=i[11],
                            actions=[
                                PostbackAction(
                                    label='營養成分',
                                    text='營養成分',
                                    data='/mealID@'+str(i[0])
                                )
                            ]
                        )
                    )

            if(len(userBroadcastMessage) >0):

                ''''''
                Carousel_template = TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=userBroadcastMessage
                    )
                )
                ''''''
                #line_bot_api.reply_message(event.reply_token, image_carousel_template_message)
                line_bot_api.reply_message(event.reply_token, Carousel_template)
            #message = FlexSendMessage(alt_text="healthInfo",contents=CarouselMsg.healthInfo(resultList, userDiseaseList))
                #line_bot_api.reply_message(event.reply_token, message)

        elif(broadcast_mode[0]=="common"):
            print("common")
            for i in broadcastMessageList:

                flag = True
                arr = re.split(r',', i[2])

                for j in arr:
                    attr = re.match(r"(\w+)\:(\d+)?\~?(\d+)?", j)
                    flag = check_filter(userData_dict, attr.groups('-1')) and flag

                if flag:

                    if (i[0] == "text"):
                        userBroadcastMessage.append(TextSendMessage(text=i[1]))
                    elif (i[0] == "image"):
                        userBroadcastMessage.append(
                            ImageSendMessage(original_content_url=host_url + i[1],
                                             preview_image_url=host_url + i[1])
                        )
                # Line only allow at most 5 messages for one function call
                if len(userBroadcastMessage) == 5:
                    break
            line_bot_api.reply_message(event.reply_token, userBroadcastMessage)


        else:
            print("wrong type")
            line_bot_api.reply_message(event.reply_token, TextSendMessage("wrong type"))


        '''        
        if len(userBroadcastMessage) >= 1:
            replyBroadcastMessage = "• " + userBroadcastMessage[0]
            if len(userBroadcastMessage) >= 2:
                for l in range(1, len(userBroadcastMessage)):
                    replyBroadcastMessage = replyBroadcastMessage + "\n• " + userBroadcastMessage[l]
        '''

        #line_bot_api.reply_message(event.reply_token, userBroadcastMessage)
        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=broadcast_mode[0]))
    '''
    if event.beacon.hwid == "":
        message = TextSendMessage(text = 'success')
    else:
        message = TextSendMessage(text = 'not this position')
    '''

# Deprecated or not?
def food_recognition(replyToken,imageUrl,dist_path):
    #googletrans API : https://pypi.org/project/googletrans/
    #problem fix: https://stackoverflow.com/questions/52455774/googletrans-stopped-working-with-error-nonetype-object-has-no-attribute-group
    translator = Translator()

    response = clarifai_model[1].predict_by_url(url=imageUrl)
    image = imageUrl.lstrip('http')
    image = 'https'+image
    print(dist_path)
    concepts = response['outputs'][0]['data']['concepts']
    actionList = []

    with open('tranlateList.csv', newline='') as csvfile:
        # 讀取 CSV 檔案內容
        rows = csv.reader(csvfile)
        # 以迴圈輸出每一列
        transTW = [
            translator.translate(concepts[0]['name'],dest='zh-TW',src='en').text,
            translator.translate(concepts[1]['name'],dest='zh-TW',src='en').text,
            translator.translate(concepts[2]['name'],dest='zh-TW',src='en').text
        ]
        
        for row in rows:
            for i in range(0,3):
                if concepts[i]['name'] in row:
                    transTW[i] = row[1]
                    break

    for i in range(0,3):
        actionList.append(PostbackAction(label= str(concepts[i]['name'])+ ' ' + transTW[i], data= transTW[i]+'@'+str(concepts[i]['name']) + '@' + dist_path))
    actionList.append(PostbackAction(label='自行輸入', data='/manual_add@'+dist_path))
    buttons_template = ButtonsTemplate(thumbnail_image_url=image, text='Result', title='辨識結果', actions=actionList)
    template_message = TemplateSendMessage(alt_text='Buttons alt text', template=buttons_template)
    line_bot_api.reply_message(replyToken, [TextSendMessage(text='您好，以下為可能的食物種類'), template_message])
    
def isNum(data):
    if len(data) > 1 and data[0] == '0': return False
    return data.replace('.', '', 1).isnumeric()

def check_filter(userData_dict, attr):
    if attr[1] == "-1":
        return True
    else:
        if userData_dict[attr[0]] >= float(attr[1]) and userData_dict[attr[0]] <= float(attr[2]):
            return True
        else:
            return False




if __name__ == "__main__":
    make_static_tmp_dir()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


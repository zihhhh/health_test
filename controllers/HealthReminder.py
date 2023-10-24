from linebot.models import *
from LineInitializer import line_bot_api, handler
import BubbleMsg
import requests
import config
import datetime as dt
from datetime import datetime
import json
import threading
import time

def healthMessage(event, jobnumber):

    def job_sport(queryTime):
        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'queryTime': queryTime
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/sport/querySportRecord.php', data=param)
        resultList = json.loads(response.text)
        print(resultList)
        return BubbleMsg.todaySport(resultList) 
    
    def sportMessage():
        messages = []
        bubble, sportTimeYesterday = job_sport(datetime.now() - dt.timedelta(hours = 24))
        bubble, sportTimeToday = job_sport(datetime.now())
        if sportTimeToday == 0:
            messages.append(TextSendMessage(text = '您今日尚無運動紀錄！'))
        
        if sportTimeYesterday == 0:
            messages.append(TextSendMessage(text = '您昨日無運動紀錄！'))

        if sportTimeYesterday + sportTimeToday >= 60:
            messages.append(TextSendMessage(text = '您昨日運動總時間' + str(sportTimeYesterday) + '分鐘\n＋今日運動總時間' + str(sportTimeToday) + '分鐘，已達到平均每日運動30分鐘的健康建議！\n請持續保持～'))
        else:
            if sportTimeYesterday > 29:
                messages.append(TextSendMessage(text = '您昨日運動總時間' + str(sportTimeYesterday) + '分鐘，已達基本量30分鐘。'))
                if sportTimeToday > 0:
                    messages.append(TextSendMessage(text = '您今日運動總時間' + str(sportTimeToday) + '分鐘，尚未達基本量30分鐘，加油～'))
            if sportTimeYesterday < 30 and sportTimeYesterday > 0:
                messages.append(TextSendMessage(text = '您昨日運動總時間' + str(sportTimeYesterday) + '分鐘，未達基本量30分鐘，建議您今日多步行移動。'))
            else:
                messages.append(TextSendMessage(text = '每日運動30分鐘維持健康。'))

        line_bot_api.push_message(event.source.user_id, messages)
    
    def job_calorie():
        meal = 4
        query_meal = ['早餐', '午餐', '晚餐', '點心']
        calcSum = 0
        while(meal != 0):
            parm = {
                'queryRecord': 'queryRecord',
                'userID': event.source.user_id,
                'meal': query_meal[4 - meal],
                'queryTime': datetime.now()
            }
            response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data = parm)
            resultList = json.loads(response.text)
            for result in resultList:
                name = result.split('@')[0]
                cal = result.split('@')[1]
                calcSum += float(cal)
            meal = meal - 1
        return calcSum

    def job_energyNeed():
        data = { 'userID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)
        if resultList['gender']=='male':
            BMR = (13.7 * float(resultList['weight'])) + (5.0 * float(resultList['height'])) - (6.8 * float(resultList['age'])) + 66
        elif resultList['gender']=='female':
            BMR = (9.6 * float(resultList['weight'])) + (1.8 * float(resultList['height'])) - (4.7 * float(resultList['age'])) + 655
    
        if resultList['workLoad'] == '臥床躺著不動':
            energyNeed = BMR * 1.2
        elif resultList['workLoad'] == '輕度工作者':
            energyNeed = BMR * 1.375
        elif resultList['workLoad'] == '中度工作者':
            energyNeed = BMR * 1.55
        elif resultList['workLoad'] == '重度工作者':
            energyNeed = BMR * 1.725
        return energyNeed, BMR
    
    def calorieMessage(): 
        energyNeed, BMR = job_energyNeed()
        calcSum = job_calorie()
        messages = [] 
        if calcSum > energyNeed:
            messages.append(TextSendMessage(text = '您今日已攝取' + str(calcSum) + '大卡，超過建議熱量攝取' + str(round(calcSum - energyNeed)) + '大卡。\n建議您今日多運動消耗熱量。'))
            #if jobnumber == 3:
            #    messages.append(TextSendMessage(text = '運動建議'))
        elif calcSum == 0:
            messages.append(TextSendMessage(text = '您今日尚無飲食紀錄，請記得紀錄飲食才能有效控制熱量。\n您一天的建議攝取熱量為' + str(round(energyNeed)) + '大卡，請均衡飲食。'))
        elif calcSum < BMR:
            messages.append(TextSendMessage(text = '您今日已攝取' + str(calcSum) + '大卡，尚少於基礎代謝率' + str(round(BMR - calcSum)) + '大卡。'))

        line_bot_api.push_message(event.source.user_id, messages)
    
    def loseweightMessage():
        energyNeed, BMR = job_energyNeed()
        calcSum = job_calorie()
        messages = []
        if calcSum > BMR:
            bubble, sportTime = job_sport(datetime.now())
            sportcalorie = sportTime/30 * 300
            energy = energyNeed - calcSum + sportcalorie
            if energy > 1300:
                messages.append(TextSendMessage(text = '今日已消耗' + str(round(energy)) + '大卡，恭喜達成今日最終目標!\n請持續保持~'))
            elif energy >500:
                messages.append(TextSendMessage(text = '今日已消耗' + str(round(energy)) + '大卡，恭喜達成今日目標!\n請持續保持~'))
            elif energy > 0:
                messages.append(TextSendMessage(text = '今日已消耗' + str(round(energy)) + '大卡，離目標還有一小段距離。\n繼續加油~'))
            else:
                messages.append(TextSendMessage(text = '您今日已攝取' + str(calcSum) + '大卡，超過基礎代謝率' + str(round(calcSum - BMR)) + '大卡。\n建議您今日多運動消耗熱量。'))
        elif calcSum == 0:
            messages.append(TextSendMessage(text = '您今日尚無飲食紀錄，請記得紀錄飲食才能有效控制熱量。\n您一天的基礎代謝率為' + str(round(BMR)) + '大卡，請均衡飲食。'))
        elif calcSum < BMR:
            messages.append(TextSendMessage(text = '您今日已攝取' + str(calcSum) + '大卡，尚少於基礎代謝率' + str(round(BMR - calcSum)) + '大卡。'))
        line_bot_api.push_message(event.source.user_id, messages)


    def job_loseweight():
        messages = []
        messages.append(TextSendMessage(text = '適當的減重速度為一星期0.5~1kg，每日約需消耗500~1300大卡。\n減重的好處: 減重可以降低糖尿病、高血壓、高血脂症、心臟病、腦中風等疾病發生的機率，讓身體更健康!'))
        line_bot_api.reply_message(event.reply_token, messages)


    
    def job_weight():
        data = { 'userID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)

        messages = []
        messages.append(TextSendMessage(text='您目前體重是'+resultList['weight']+'kg嗎?'))
        button = ButtonsTemplate(title='體重: '+resultList['weight']+' kg', text='更新紀錄', actions=[
            PostbackAction(label='更新體重', data='/weight'),
            PostbackAction(label='取消', data='/cancel')
        ])
        messages.append(TemplateSendMessage(alt_text='Buttons alt text', template=button))
        line_bot_api.push_message(event.source.user_id, messages)
            
    def set_interval(func, sec):
        def func_wrapper():
            set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t
    
    if jobnumber == 0:
        sportMessage()
        # set_interval(sortMessage, 86400)
    elif jobnumber == 1:
        calorieMessage()
        # set_interval(calorieMessage, 21600)
    elif jobnumber == 2:
        sportMessage()
        # set_interval(sportMessage, 21600)
        # set_interval(calorieMessage, 86400)
    elif jobnumber == 3:
        job_loseweight()
        loseweightMessage()
        job_weight()
        # set_interval(loseweightMessage, 21600)
        # set_interval(job_weight, 86400*14)
    
    # one day = 86400 sec


class HealthReminder():
    def __init__(self):
        pass
    
    @staticmethod
    def sportReminder(event):
        jobnumber = 0
        healthMessage(event, jobnumber)
    
    @staticmethod
    def calorieReminder(event):
        jobnumber = 1
        healthMessage(event, jobnumber)
    
    @staticmethod
    def keepHealth(event):
        jobnumber = 2
        healthMessage(event, jobnumber)

    @staticmethod
    def loseWeight(event):
        jobnumber = 3
        healthMessage(event, jobnumber)

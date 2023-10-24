from linebot.models import *
from LineInitializer import line_bot_api, handler
import requests
import BubbleMsg
import config
import datetime as dt
from datetime import datetime
import json


class DietRecordController():
    def __init__(self):
        pass
    
    @staticmethod
    def askDietRecord(event):
        day = 0
        meal = 4
        query_meal = ['早餐', '午餐', '晚餐', '點心']
        day_text = ['今日', '昨日', '前天']
        query_day = [0, 24, 48]

        if('今' in event.message.text):
            day = 0
        elif('昨' in event.message.text):
            day = 1
        elif('前' in event.message.text):
            day = 2
        
        if('早' in event.message.text):
            meal = 0
        elif('午' in event.message.text):
            meal = 1
        elif('晚' in event.message.text):
            meal = 2
        elif('心' in event.message.text):
            meal = 3
        else:
            meal = 4 # all day
        
        message = []
        if(meal == 4):
            while(meal != 0):
                parm = {
                    'queryRecord': 'queryRecord',
                    'userID': event.source.user_id,
                    'meal': query_meal[4 - meal],
                    'queryTime': datetime.now() - dt.timedelta(hours = query_day[day])
                }
                response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data = parm)
                resultList = json.loads(response.text)
                message.append(FlexSendMessage(alt_text=day_text[day] + query_meal[4 - meal] + '紀錄', contents=BubbleMsg.todayDiet(query_meal[ 4 - meal], resultList, day_text[day])))
                meal = meal - 1
        else:
            parm = {
                'queryRecord': 'queryRecord',
                'userID': event.source.user_id,
                'meal': query_meal[meal],
                'queryTime': datetime.now() - dt.timedelta(hours = query_day[day])
            }
            response = requests.post(config.PHP_SERVER+'mhealth/food/queryFoodRecord.php', data = parm)
            resultList = json.loads(response.text)
            message = FlexSendMessage(alt_text=day_text[day] + query_meal[meal] + '紀錄', contents=BubbleMsg.todayDiet(query_meal[meal], resultList, day_text[day]))
        
        line_bot_api.reply_message(event.reply_token, message)

        
        
        

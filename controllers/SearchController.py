from linebot.models import ( FlexSendMessage, ButtonsTemplate, TextSendMessage,
    URITemplateAction, TemplateSendMessage, PostbackAction, ImageSendMessage)
from LineInitializer import line_bot_api, handler
import requests
from datetime import datetime
import json
import BubbleMsg, CarouselMsg

import config
import constant
import utility

class SearchController():
    def __init__(self):
        pass

    # TODO: language implementation
    @staticmethod
    def searchDietToday(event):
        dietC = ['早餐', '午餐', '晚餐', '點心']
        dietE = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
        diet = [dietC, dietE]
        lang = 0
        param = {
            'queryRecordAll': 'queryRecordAll',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/food/queryFoodRecord.php', data=param)
        resultList = json.loads(response.text)
        currentCal = 0.0
        for result in resultList:
            # "name carolie fat sugar fiber"
            currentCal += float(result.split('@')[1])
        roundCal = round(float(currentCal), 1)

        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlFood, title='今日飲食', text=str(roundCal)+' kcal', actions=[
            PostbackAction(label=diet[lang][0], data='/breakfast'),
            PostbackAction(label=diet[lang][1], data='/lunch'),
            PostbackAction(label=diet[lang][2], data='/dinner'),
            PostbackAction(label=diet[lang][3], data='/snack')
        ])
        allMessage = [TemplateSendMessage(alt_text='今日飲食', template=buttons_template)]
        allMessage += utility.FoodRecordRecommend(event.source.user_id, None)
        line_bot_api.reply_message(event.reply_token, allMessage)

    @staticmethod
    def searchSportToday(event):
        messages = []
        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/sport/querySportRecord.php', data=param)
        resultList = json.loads(response.text)
        print(resultList)
        bubble, sportTime = BubbleMsg.todaySport(resultList) 
        messages.append(FlexSendMessage(alt_text="今日運動", contents=bubble))

        if sportTime < 30 :
            messages.append(TextSendMessage(text = '今日運動總時間' + str(sportTime) + '分鐘，還未達基本量30分鐘。'))

        line_bot_api.reply_message(event.reply_token, messages)

    @staticmethod
    def searchBloodPressureToday(event):
        messages = []
        data = {
            'queryInfo': 'pulse',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER+'mhealth/info/queryInfo.php', data=data)
        resultList = json.loads(response.text)
        print(resultList)
        bubble, highpressureTimes, lowpressureTimes = BubbleMsg.todayPressure(resultList)
        messages.append(FlexSendMessage(alt_text="今日血壓", contents=bubble))

        if highpressureTimes > 0:
            messages.append(TextSendMessage(text = '您今日有' + str(highpressureTimes) + '次血壓偏高，請注意。'))
        elif lowpressureTimes > 0:
            messages.append(TextSendMessage(text = '您今日有' + str(lowpressureTimes) + '次血壓偏低，請注意。'))

        line_bot_api.reply_message(event.reply_token, messages)

    @staticmethod
    def searchWaterToday(event):
        messages = []
        data = {
            'queryInfo': 'water',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/info/queryInfo.php', data = data)
        resultList = json.loads(response.text)
        print(resultList)
        bubble, totalsum = BubbleMsg.todayWater(resultList)
        messages.append(FlexSendMessage(alt_text="今日飲水", contents=bubble))
        
        data = { 'userID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)
        waterToDrink = (float(resultList['weight']) + float(resultList['height'])) * 10
        if totalsum < waterToDrink :
            messages.append(TextSendMessage(text = '今日總飲水量' + str(totalsum) + '毫升，還未達基本量' + str(waterToDrink) + '毫升。'))

        line_bot_api.reply_message(event.reply_token, messages)

    @staticmethod
    def searchTempToday(event):
        data = {
            'queryInfo': 'temperature',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/info/queryInfo.php', data = data)
        resultList = json.loads(response.text)
        print(resultList)
        message = FlexSendMessage(alt_text="今日體溫", contents=BubbleMsg.todayTemprature(resultList))
        line_bot_api.reply_message(event.reply_token, message)

    @staticmethod
    def caloriegraph(event):
        param = {
            'getGraph': 'calorie',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/graph/calorie.php', data=param)
        print(response.text)
        image_message = ImageSendMessage(original_content_url = response.text[:-1], preview_image_url = response.text[:-1])
        line_bot_api.reply_message(event.reply_token, image_message)

    @staticmethod
    def dietgraph(event):
        param = {
            'getGraph': 'diet',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/graph/diet.php', data=param)
        print(response.text)
        image_message = ImageSendMessage(original_content_url = response.text[:-1], preview_image_url = response.text[:-1])
        line_bot_api.reply_message(event.reply_token, image_message)

    @staticmethod
    def sportgraph(event):
        param = {
            'getGraph': 'sport',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/graph/sport.php', data=param)
        print(response.text)
        image_message = ImageSendMessage(original_content_url = response.text[:-1], preview_image_url = response.text[:-1])
        line_bot_api.reply_message(event.reply_token, image_message)
    
    @staticmethod
    def temperaturegraph(event):
        param = {
            'getGraph': 'temperature',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/graph/temperature.php', data=param)
        print(response.text)
        image_message = ImageSendMessage(original_content_url = response.text[:-1], preview_image_url = response.text[:-1])
        line_bot_api.reply_message(event.reply_token, image_message)

    @staticmethod
    def watergraph(event):
        messages = []
        param = {
            'getGraph': 'water',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/graph/water_warn.php', data=param)
        resultList = json.loads(response.text)
        print(resultList)
        messages.append(ImageSendMessage(original_content_url = resultList['GraphURL'], preview_image_url = resultList['GraphURL']))
        if resultList['HasWarn'] == 1:
            messages.append(TextSendMessage(text = resultList['HealthWarn']))
        line_bot_api.reply_message(event.reply_token, messages)
    
    @staticmethod
    def pressuregraph(event):
        messages = []
        param = {
            'getGraph': 'pressure',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/graph/blood_pressure_warn.php', data=param)
        resultList = json.loads(response.text)
        print(resultList)
        messages.append(ImageSendMessage(original_content_url = resultList['GraphURL'], preview_image_url = resultList['GraphURL']))
        if resultList['HasWarn'] == 1:
            messages.append(TextSendMessage(text = resultList['HealthWarn']))
        line_bot_api.reply_message(event.reply_token, messages)
    
    @staticmethod
    def recordOverview(event):
        data = { 'userID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        userInfoList = json.loads(response.text)

        data = {'lineID' : event.source.user_id}
        response = requests.post(config.PHP_SERVER+'mhealth/disease/queryUserDisease.php', data = data)
        userDiseaseList = json.loads(response.text)

        data = {
            'queryInfo': 'pulse',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER+'mhealth/info/queryInfo.php', data=data)
        userBPList = json.loads(response.text)

        data = {
            'queryInfo': 'temperature',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/info/queryInfo.php', data = data)
        userTemperatureList = json.loads(response.text)

        data = {
            'queryInfo': 'water',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/info/queryInfo.php', data = data)
        resultList = json.loads(response.text)
        bubble, waterSum = BubbleMsg.todayWater(resultList)

        param = {
            'queryRecord': 'queryRecord',
            'userID': event.source.user_id,
            'queryTime': datetime.now()
        }
        response = requests.post(config.PHP_SERVER + 'mhealth/sport/querySportRecord.php', data=param)
        resultList = json.loads(response.text)
        print(resultList)
        bubble, sportTime = BubbleMsg.todaySport(resultList) 
        
        meal = 4
        query_meal = ['早餐', '午餐', '晚餐', '點心']
        calorieSum = 0
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
                calorieSum += float(cal)
            meal = meal - 1

        messages = FlexSendMessage(alt_text="healthInfo", contents=BubbleMsg.recordOverview(userInfoList, userDiseaseList, userBPList, userTemperatureList, calorieSum, waterSum, sportTime))
        line_bot_api.reply_message(event.reply_token, messages)
    
    @staticmethod
    def bubbleMsg(event):
        messages = []
        messages.append(FlexSendMessage(alt_text="query_record", contents=BubbleMsg.queryRecord()))
        line_bot_api.reply_message(event.reply_token, messages)
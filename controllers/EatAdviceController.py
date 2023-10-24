from linebot.models import FlexSendMessage, TextSendMessage
from components.EatAdviceMessage import EatAdvice, EatAdviceMessage
from LineInitializer import line_bot_api, handler
import requests

class EatAdviceController():
    def __init__(self):
        pass
    
    @staticmethod
    def replyAdviceMessage(event):
        eatAdviceMessage = EatAdviceMessage(280)
        eatAdviceMessage.addAdvice(EatAdvice('日荃蒸餃', '蒸餃', 350, 40, 'https://i.imgur.com/UG0LQrx.png'))
        eatAdviceMessage.addAdvice(EatAdvice('大呼過癮', '泡菜臭臭鍋', 1000, 110, 'https://i.imgur.com/mkMPU1R.png'))
        eatAdviceMessage.addAdvice(EatAdvice('三商巧福', '紅燒排骨飯', 650, 139, 'https://imgur.com/zKAO8T0.png'))
        message = FlexSendMessage(alt_text="飲食建議", contents=eatAdviceMessage.buildComponent())
        line_bot_api.reply_message(event.reply_token, message)

    @staticmethod
    def askForFood(event):
        if ('吃' in event.message.text):
            food = event.message.text.split('吃')[1]
            eatDrink = '吃'
        elif ('喝' in event.message.text):
            food = event.message.text.split('喝')[1]
            eatDrink = '喝'
        if (food[-1] == '嗎'):
            food = food[:-1]
        diseases = requests.get('https://mhealth-service.feveral.me/api/food/disease', verify=False, params={
            'lineID': event.source.user_id,
            'food': food
        }).json()['diseases']
        if len(diseases) == 0:
            message = [TextSendMessage(text='請放心食用!')]
        else:
            message = [TextSendMessage(text='您有' + '和'.join(diseases) + '\n不適合' + eatDrink + ' ' + food)]
        line_bot_api.reply_message(event.reply_token, message)
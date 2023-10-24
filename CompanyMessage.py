import re
import requests
import json
from linebot.models import *
import string
import config
# line_bot_api = LineBotApi('eeca7lo2Ebs14wFbm4AXhvU/5qj569ywDfMxQ9a4cZaIqDKE4TFiHNNWvUaah2A2clVoV9McprdK6K/guNEZiSV8P6+HRgPr2Z3mB+3it2r3q2IDUJByKbPMoGwTrduDjjXZiW5xAp2FWQzSC0Tc7wdB04t89/1O/w1cDnyilFU=')
# line_bot_api.push_message('U81aa8a8d31959c94187c4869bb1eeddf', TextSendMessage(text = 'push message'))
# https://cdn4.iconfinder.com/data/icons/coronavirus-color/64/doctor-advise-warning-suggestion-avatar-1024.png
def PushMessage(line_bot_api, to, text):

    data = { 'userID' : to}
    response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
    resultList = json.loads(response.text)
    user_name = resultList['name']

    msg = [TextComponent(text = "Dear " + user_name + " :"),
        TextComponent(text = text, weight='bold', color='#cd5c5c')]
    if text == "Your health risk is high.":
        msg.append(TextComponent(text = "You should take good care of"))
        msg.append(TextComponent(text = "yourself and pay more attention to"))
        msg.append(TextComponent(text = "your health."))
    elif text == "Your health risk is medium.":
        msg.append(TextComponent(text = "You should take good care of"))
        msg.append(TextComponent(text = "yourself."))
    else:
        msg.append(TextComponent(text = "Keep going !"))

    bubble = BubbleContainer(
        direction = 'ltr',
        body = BoxComponent(
            layout = 'vertical',
            contents = [
                BoxComponent(
                    layout = 'vertical',
                    contents = [
                        TextComponent(text = "Health Risk", weight='bold', size='xl', color='#000000')
                    ]
                ),
                BoxComponent(
                    layout = 'vertical',
                    contents = [
                        ImageComponent(url = 'https://cdn4.iconfinder.com/data/icons/coronavirus-color/64/doctor-advise-warning-suggestion-avatar-1024.png')
                    ]
                ),
                BoxComponent(
                    layout = 'vertical',spacing='md',margin='xl',
                    contents = msg
                )
            ]
        )
    )
    message = FlexSendMessage(alt_text = 'Company Health Platform Message', contents = bubble) 
    line_bot_api.push_message(to, message)

def HealthRank(user_lineID, result):
    comp = []
    comp.append(TextComponent(text = "No." + "       " + "name" + "                  " + "value", color="#000000", flex=0))
    i = 0
    value = result["sortedData"]
    length = len(value)
    lineIDList = result["lineIDList"][0]
    title = result["category"]

    for i in range(length):
        lineID = lineIDList[i]
        color = '#000000'
        space = "             "

        data = { 'userID' : lineID}
        response = requests.post(config.PHP_SERVER+'mhealth/lineUser/queryUserInfo.php', data = data)
        resultList = json.loads(response.text)
        user_name = resultList['name']

        if lineID == user_lineID:
            color = '#4169E1'
        if i == 0:
            color = '#ffa500'
        if value[i] < 0:
            space = "           "

        comp.append(TextComponent(text = str(i+1) + ".      " + user_name + space + str(value[i]), size = 'xl', color=color, flex=0))
        i+=1

    for i in range(len(result["category"])):
        if result["category"][i].isupper():
            title = result["category"][:i] + ' ' + result["category"][i:] + ' '+ 'Rank'
    title = string.capwords(title)

    bubble = BubbleContainer(
        direction = 'ltr',
        body = BoxComponent(
            layout = 'vertical',
            contents = [BoxComponent(
                layout = 'vertical',
                contents = [
                    TextComponent(text=title, weight='bold', size='xl', color='#000000')
                ]
            ),
            BoxComponent(
                layout='vertical',spacing='md',margin='lg',
                contents=comp
            )
            ]
        )
    )
    return bubble
    

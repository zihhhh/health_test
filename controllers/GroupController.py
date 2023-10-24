from linebot.models import *
from LineInitializer import line_bot_api, handler
import requests
import config

class GroupController():

    # Just a demo version
    @staticmethod
    def groupTarget(event):
        calorie1 = 1536
        imageUrl = 'https://i.imgur.com/lTKzLp9.png'
        components = []
        components.append(
            BoxComponent(
                layout='vertical',
                contents= [
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='楊宗翰今日已攝取 ', weight='bold', flex=0, size='xs', color='#555555'),
                            TextComponent(text=str(calorie1), weight='bold', flex=0, size='xs', color='#ff0000'),
                            TextComponent(text=' 大卡', weight='bold', size='xs', flex=0, color='#555555')
                        ]
                    ),
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='李真華今日還', weight='bold', flex=0, size='sm', color='#555555'),
                            TextComponent(text='未登錄晚餐。', weight='bold', flex=0, size='sm', color='#ff0000'),
                        ]
                    ),
                ]
            )
        )
        components.append(            
            BoxComponent(
                layout='vertical',spacing='xs',margin='xl',
                contents=[
                    ImageComponent(url=imageUrl, margin='none',align='center',size='xxl'),
                    ButtonComponent(style='link', height='sm', size='xs', action=URIAction(label='點此登錄', uri=config.ADD_FOOD_MANUALLY_LIFF_URI)),
                ]
            )
        )
        container = BubbleContainer(
            direction='ltr',
            body=BoxComponent( layout='vertical', contents=components)
        )

        templateMessage = TemplateSendMessage(
            alt_text='Buttons Template',
            template=ButtonsTemplate(
                title='群組目標',
                text='楊宗翰今日已攝取 1536 大卡\n李真華今日還未登錄晚餐\n',
                thumbnail_image_url=imageUrl,
                actions=[
                    URITemplateAction(
                        label='辨識結果',
                        uri=config.ADD_FOOD_MANUALLY_LIFF_URI
                    )
                ]
            )
        )

        message = FlexSendMessage(alt_text="飲食建議", contents=container)
        line_bot_api.reply_message(event.reply_token, templateMessage)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
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

import config

def newRecord():
    message = ImagemapSendMessage(
        base_url='https://i.imgur.com/t5E9wz1.png',
        alt_text='this is an imagemap',
        base_size=BaseSize(height=694, width=1040),
        actions=[
            URIImagemapAction(
                link_uri=config.ADD_FOOD_MANUALLY_LIFF_URI,
                area=ImagemapArea(
                    x=0, y=0, width=346, height=346
                )
            ),
            MessageImagemapAction(
                text='新增運動',
                area=ImagemapArea(
                    x=346, y=0, width=346, height=346
                )
            ),
            MessageImagemapAction(
                text='新增飲水',
                area=ImagemapArea(
                    x=692, y=0, width=346, height=346
                )
            ),
            MessageImagemapAction(
                text='新增血壓',
                area=ImagemapArea(
                    x=0, y=346, width=346, height=346
                )
            ),
            MessageImagemapAction(
                text='新增體溫',
                area=ImagemapArea(
                    x=346, y=346, width=346, height=346
                )
            ),
            MessageImagemapAction(
                text='新增返回',
                area=ImagemapArea(
                    x=692, y=692, width=346, height=346
                )
            )
        ]
    )
    return message

def healthKeeper():
    message = ImagemapSendMessage(
        base_url='https://i.imgur.com/962LknF.png',
        alt_text='Health keeper imagemap',
        base_size=BaseSize(height=600, width=1040),
        actions=[
            MessageImagemapAction(
                text='飲食順序',
                area=ImagemapArea(
                    x=0, y=0, width=1040, height=300
                )
            ),
            MessageImagemapAction(
                text='健康資訊',
                area=ImagemapArea(
                    x=0, y=300, width=1040, height=300
                )
            ),
        ]
    )
    return message
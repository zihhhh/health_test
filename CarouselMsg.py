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
    FlexSendMessage, BubbleContainer, CarouselContainer,ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton, ImagemapSendMessage, BaseSize,
    URIImagemapAction, ImagemapArea, MessageImagemapAction
)
import requests
import config
import json

RED = '#CD1D01'
GREEN = '#09AC1B'
ORANGE = '#EB8F28'
GRAY = '#555555'
BLACK = '#111111'
BLUE = '#299EEA'
WHITE = '#FFFFFF'
DEBUG = 1

def healthInfo(resultList, userDiseaseList):
  userGender = ''
  userEatingHabit = ''
  waterToDrink = 0
  energyNeed = 0
  BMR = 0
  standardWeight = 0
  BMI = dict()
  fatRate = dict()

  BMI['value'] = round(float(resultList['weight'])/((float(resultList['height'])/100)**2),1)

  # Set body fat rate
  if resultList['bodyFatRate'] is None:
    fatRate['value'] = "未設定"
  else:
    fatRate['value'] = float(resultList['bodyFatRate'])
  if DEBUG:
    print('fatRate["value"]: ', fatRate['value'])

  # Calculate daily water requirement by age
  if int(resultList['age']) < 30:
    waterToDrink = float(resultList['weight'])*40
  elif int(resultList['age']) >= 30 and int(resultList['age']) <= 55:
    waterToDrink = float(resultList['weight'])*35
  elif int(resultList['age']) > 55:
    waterToDrink = float(resultList['weight'])*30
  if DEBUG:
    print('resultList["age"]: ', int(resultList['age']))
    print('waterToDrink: ', waterToDrink)

  # BMI level
  if BMI['value'] < 18.5:
    BMI['level'] = '過輕'
    BMI['color'] = BLUE
  elif BMI['value'] <= 24 and BMI['value'] >= 18.5:
    BMI['level'] = '正常'
    BMI['color'] = GREEN
  elif BMI['value'] >= 24 and BMI['value'] < 27:
    BMI['level'] = '過重'
    BMI['color'] = ORANGE
  elif BMI['value'] >= 27 and BMI['value'] < 30:
    BMI['level'] = '輕度肥胖'
    BMI['color'] = RED
  elif BMI['value'] >= 30 and BMI['value'] < 35:
    BMI['level'] = '中度肥胖'
    BMI['color'] = RED
  elif BMI['value'] >= 35:
    BMI['level'] = '重度肥胖'
    BMI['color'] = RED
  if DEBUG:
    print("BMI['level']: ", BMI['level'])
    print("BMI['color']: ", BMI['color'])

  #=====classify fatRate========
  if resultList['gender']=='male':
    userGender = '男'
    if fatRate['value'] == "未設定":
      fatRate['level'] = "請設定體脂率"
      fatRate['color'] = GRAY
    elif int(resultList['age']) <= 30:
      if fatRate['value'] >= 20:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
    elif int(resultList['age']) > 30:
      if fatRate['value'] >= 25:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
  elif resultList['gender']=='female':
    userGender = '女'
    if fatRate['value'] == "未設定":
      fatRate['level'] = "請設定體脂率"
      fatRate['color'] = RED
    elif int(resultList['age']) <= 30:
      if fatRate['value'] >= 25:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
    elif int(resultList['age']) > 30:
      if fatRate['value'] >= 30:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
  if DEBUG:
    print('fatRate level: ', fatRate['level'])
    print('fatRate color: ', fatRate['color'])
    print('fatRate value: ', fatRate['value'])
  #=====end of classify fatRate========
  

  #===== calculate energy need per day ======
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
  
  if DEBUG:
    print('workload: ', resultList['workLoad'])
    print('BMR: ', BMR)
    print('energyNeed: ', energyNeed)
  #===== end of calculate energy need per day ======

  #===== calculate standard weight =======
  if resultList['gender']=='male':
    standardWeight = (float(resultList['height']) - 170)*0.6 + 62
  elif resultList['gender']=='female':
    standardWeight = (float(resultList['height']) - 158)*0.5 + 52
  if DEBUG:
      print('standardWeight: ', standardWeight)
  #===== end of calculate standard weight =======


  if resultList['eatingHabit'] == 'meat':
    userEatingHabit = '葷食'
  elif resultList['eatingHabit'] == 'vagetarian':
    userEatingHabit = '素食'
  else:
    userEatingHabit = '請設定飲食習慣'
  if DEBUG:
    print('userEatingHabit: ', userEatingHabit)

  #======== user disease ================
  userDisease = []
  diseaseBoxList = []
  if len(userDiseaseList) == 0:
    userDisease.append(TextComponent(text='無', weight='bold', size='sm', color=GRAY,  align='start'))
    diseaseBoxList.append(TextComponent(text='無特殊疾病', weight='bold', size='sm', color=BLACK,  align='start'))
  elif len(userDiseaseList) != 0:
    for row in userDiseaseList:
      userDisease.append(TextComponent(text=row['disease'], weight='bold', size='sm', color=GRAY,  align='start'))
      data = {
        'disease':row['disease']
      }
      response = requests.post(config.PHP_SERVER+'mhealth/disease/queryDiseaseDict.php', data=data)
      diseaseIntro = json.loads(response.text)
      boxSuggest  = [TextComponent(text=row['disease'], weight='bold', size='sm', color=BLACK)]
      if diseaseIntro[0]['suggest']:
        boxSuggest.append(TextComponent(text='建議', weight='bold', size='sm', color=GREEN,  align='start'))
        for i in diseaseIntro[0]['suggest'].split('@'):
          boxSuggest.append(TextComponent(text=i, weight='bold', size='xs', color=GRAY, align='start'))
      if diseaseIntro[0]['neverDo']:
        boxSuggest.append(TextComponent(text='禁忌', weight='bold', size='sm', color=RED,  align='start'))
        for i in diseaseIntro[0]['neverDo'].split('@'):
          boxSuggest.append(TextComponent(text=i, weight='bold', size='xs', color=GRAY, align='start'))
      boxSuggest.append(SeparatorComponent(margin='sm'))
      box = BoxComponent(
              layout='vertical',
              contents= boxSuggest
            )
      diseaseBoxList.append(box)
  if DEBUG:
    print('userDisease: ', userDisease)
    print('diseaseBoxList: ', diseaseBoxList)
  #======== end of user disease ==========

  energyContent = [
    BoxComponent(
      layout='horizontal',
      contents=[
        TextComponent(text='每日身體所需熱量', weight='bold', size='sm', color=BLACK),
        TextComponent(text= str(int(energyNeed))+' 大卡', weight='bold', size='sm', color=GRAY,  align='start'),
      ],
    ),
    TextComponent(text= '基礎代謝率為 '+str(int(BMR))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start'),
    TextComponent(text= '所以每日所需總熱量為 '+str(int(energyNeed))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start'),
  ]
  if DEBUG:
    print('energyContent Default: ', energyContent)
  
  if BMI['level'] == '過輕':
    energyContent = [
      BoxComponent(
        layout='horizontal',
        contents=[
          TextComponent(text='每日身體所需熱量', weight='bold', size='sm', color=BLACK),
          TextComponent(text= str(int(energyNeed*1.1))+' 大卡', weight='bold', size='sm', color=GRAY,  align='start'),
        ],
      ),
      TextComponent(text= '基礎代謝率為 '+str(int(BMR))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start'),
      TextComponent(text= '因你為'+resultList['workLoad']+'且過輕', weight='bold', size='xs', color=GRAY,  align='start'),
      TextComponent(text= '因此建議每日攝取熱量為 '+str(int(energyNeed*1.1))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start')
    ]
  elif BMI['level'] == '正常':
    energyContent = [
      BoxComponent(
        layout='horizontal',
        contents=[
          TextComponent(text='每日身體所需熱量', weight='bold', size='sm', color=BLACK),
          TextComponent(text= str(int(energyNeed))+' 大卡', weight='bold', size='sm', color=GRAY,  align='start'),
        ],
      ),
      TextComponent(text= '基礎代謝率為 '+str(int(BMR))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start'),
      TextComponent(text= '因你為'+resultList['workLoad']+'且BMI正常', weight='bold', size='xs', color=GRAY,  align='start'),
      TextComponent(text= '因此建議每日攝取熱量為 '+str(int(energyNeed))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start')
    ]
  elif BMI['level'] == '過重' or BMI['level'] == '輕度肥胖' or BMI['level'] == '中度肥胖' or BMI['level'] == '重度肥胖':
    energyContent = [
      BoxComponent(
        layout='horizontal',
        contents=[
          TextComponent(text='每日身體所需熱量', weight='bold', size='sm', color=BLACK),
          TextComponent(text= str(int(energyNeed*0.9))+' 大卡', weight='bold', size='sm', color=GRAY,  align='start'),
        ],
      ),
      TextComponent(text= '基礎代謝率為 '+str(int(BMR))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start'),
      TextComponent(text= '因你為'+resultList['workLoad']+'且過重', weight='bold', size='xs', color=GRAY,  align='start'),
      TextComponent(text= '因此建議每日攝取熱量為 '+str(int(energyNeed*0.9))+' 大卡', weight='bold', size='xs', color=GRAY,  align='start')
    ]
  if DEBUG:
      print('energyContent by BMI: ', energyContent)

  if DEBUG:
    print("before dynamicContent")
  dynamicContent = [
    BoxComponent(
      layout='vertical',
      spacing='md',
      contents=[
        TextComponent(text='個人資料', weight='bold',size='lg', color=GREEN, align='center'),
        SeparatorComponent(margin='md'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='性別', weight='bold', size='sm', color=BLACK),
            TextComponent(text=userGender, weight='bold', size='sm', color=GRAY, align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='年齡', weight='bold', size='sm', color=BLACK),
            TextComponent(text=resultList['age']+' 歲', weight='bold', size='sm', color=GRAY, align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='身高', weight='bold', size='sm', color=BLACK),
            TextComponent(text=resultList['height']+' 公分', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='體重', weight='bold', size='sm', color=BLACK),
            TextComponent(text=resultList['weight']+' 公斤', weight='bold', size='sm', color=GRAY, align='start')
          ],
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='建議之標準體重', weight='bold', size='sm', color=BLACK),
            TextComponent(text= str(int(standardWeight)) +' 公斤', weight='bold', size='sm', color=GRAY, align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='BMI', weight='bold', size='sm', color=BLACK),
            BoxComponent(
              layout='vertical',
              contents=[
                TextComponent(text=str(BMI['value']), weight='bold', size='sm', color=GRAY, align='start'),
                TextComponent(text=BMI['level'], weight='bold', size='sm', color=BMI['color'], align='start'),
              ]
            ),
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='工作量', weight='bold', size='sm', color=BLACK),
            TextComponent(text=resultList['workLoad'], weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='疾病', weight='bold', size='sm', color=BLACK),
            BoxComponent(
              layout='vertical',
              contents=userDisease
            ),
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='飲食習慣', weight='bold', size='sm', color=BLACK),
            TextComponent(text=userEatingHabit, weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='期望改善身體目標', weight='bold', size='sm', color=BLACK),
            BoxComponent(
              layout='vertical',
              contents=[
                TextComponent(text='降低體脂率', weight='bold', size='sm', color=GRAY, align='start'),
                TextComponent(text='充足睡眠', weight='bold', size='sm', color=GRAY, align='start')
              ]
            )
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='每次運動時間', weight='bold', size='sm', color=BLACK),
            TextComponent(text='30分鐘～1小時', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='每週運動次數', weight='bold', size='sm', color=BLACK),
            TextComponent(text='1-2次', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='體脂率', weight='bold', size='sm', color=BLACK),
            BoxComponent(
              layout='vertical',
              contents=[
                TextComponent(text= str(fatRate['value']), weight='bold', size='sm', color=GRAY,  align='start'),
                TextComponent(text=fatRate['level'], weight='bold', size='sm', color=fatRate['color'], align='start')
              ]
            ),
            
          ],
        ),
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if DEBUG:
    print("before dynamicContent2")
  dynamicContent2 = [
    BoxComponent(
      layout='vertical',
      spacing='md',
      contents=[
        TextComponent(text='健康建議', weight='bold',size='lg', color=GREEN, align='center'),
        SeparatorComponent(margin='md'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='每日建議攝取水分', weight='bold', size='sm', color=BLACK),
            TextComponent(text= str(int(waterToDrink)) +' 毫升', weight='bold', size='sm', color=GRAY,  align='start'),
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='vertical',
          contents=energyContent,
        ),
        SeparatorComponent(margin='sm'),
        *diseaseBoxList,
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if DEBUG:
    print("before bubble")
  bubble = BubbleContainer(
    direction='ltr',
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  if DEBUG:
    print("before bubble2")
  bubble2 = BubbleContainer(
    direction='ltr',
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent2
    )
  )
  if DEBUG:
    print("before carousel")
  carousel = CarouselContainer(
    contents=[bubble,bubble2]
  )
  return carousel
# end of healthInfo

def changeDisease(userDiseaseList):
  userDisease = "目前疾病: "
  for row in userDiseaseList:
    userDisease+=row['disease']+' '

  box1 = BoxComponent(
    layout='horizontal',
    contents=[TextComponent(text=userDisease, weight='bold',size='sm', color=GRAY, align='start')]
  )

  dynamicContent = [
    TextComponent(text='更改個人疾病', weight='bold',size='lg', color=BLACK, align='start'),
    box1,
    SeparatorComponent(margin='md'),
  ]

  response = requests.post(config.PHP_SERVER+'mhealth/disease/queryDiseaseDict.php',)
  resultList = json.loads(response.text)
  for row in resultList:
    dynamicContent.append(
      ButtonComponent(
        style='link',
        height='sm',
        action=PostbackAction(label=row['disease'], data='/changeDisease@'+row['disease'])
      )
    )
  dynamicContent.append(
    ButtonComponent(
      style='link',
      height='sm',
      action=PostbackAction(label='取消', data='/changeDisease@'+'cancel')
    )
  )
  bubble = BubbleContainer(
    direction='ltr',
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  carousel = CarouselContainer(
    contents=[bubble]
  )
  return carousel
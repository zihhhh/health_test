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

import config
import requests
import json

RED = '#CD1D01'
GREEN = '#09AC1B'
ORANGE = '#EB8F28'
GRAY = '#555555'
BLACK = '#111111'
BLUE = '#299EEA'
WHITE = '#FFFFFF'
DEBUG = 1

def todayWater(resultList):
  calcSum = 0.0
  dynamicContent = [
    BoxComponent(
      layout='horizontal',
      contents=[
        TextComponent(text='時間', weight='bold', size='sm', color='#555555'),
        TextComponent(text='飲水量(ml)', weight='bold', size='sm', color='#111111', align='end')
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if not resultList:
    pass
  else:
    for result in resultList:
      water = result.split('@')[0]
      time = result.split('@')[1].split('.')[0]
      calcSum += float(water)
      dynamicContent.append(
        BoxComponent(
          layout='horizontal',
          margin='md',
          contents=[
            TextComponent(text=time[11:16], size='sm', color='#555555'),
            TextComponent(text=water, size='sm', color='#111111', align='end')
          ]
        )
      )
    dynamicContent.append(SeparatorComponent(margin='md'))
  dynamicContent.append(
    BoxComponent(
      layout='horizontal',
      margin='md',
      contents=[
        TextComponent(text='total', size='sm', color='#555555'),
        TextComponent(text=str(calcSum), size='sm', color='#111111', align='end')
      ]
    )
  )
      
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text='今日飲水量', weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble, calcSum

def todayTemprature(resultList):
  dynamicContent = [
    BoxComponent(
      layout='horizontal',
      contents=[
        TextComponent(text='時間', weight='bold', size='sm', color='#555555'),
        TextComponent(text='溫度(℃)', weight='bold', size='sm', color='#111111', align='end')
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if not resultList:
    dynamicContent.append(
      BoxComponent(
        layout='horizontal',
        margin='md',
        contents=[
          TextComponent(text='無紀錄', size='sm', color='#555555'),
          TextComponent(text='-', size='sm', color='#111111', align='end')
        ]
      )
    )
  else:
    for result in resultList:
      temperature = result.split('@')[0]
      time = result.split('@')[1].split('.')[0]
      dynamicContent.append(
        BoxComponent(
          layout='horizontal',
          margin='md',
          contents=[
            TextComponent(text=time[11:16], size='sm', color='#555555'),
            TextComponent(text=temperature, size='sm', color='#111111', align='end')
          ]
        )
      )   
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text='今日體溫', weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble

def todayPressure(resultList):
  highpressureTimes = 0
  lowpressureTimes = 0
  dynamicContent = [
    BoxComponent(
      layout='horizontal',
      contents=[
        TextComponent(text='時間', weight='bold', size='sm', color='#555555'),
        TextComponent(text='血壓(mmhg)', weight='bold', size='sm', color='#111111', align='end'),
        TextComponent(text='脈搏', weight='bold', size='sm', color='#111111', align='end')
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if not resultList:
    dynamicContent.append(
      BoxComponent(
        layout='horizontal',
        margin='md',
        contents=[
          TextComponent(text='無紀錄', size='sm', color='#555555'),
          TextComponent(text='-', size='sm', color='#111111', align='end'),
          TextComponent(text='-', size='sm', color='#111111', align='end')
        ]
      )
    )
  else:
    for result in resultList:
      sbp = result.split('@')[0]
      dbp = result.split('@')[1]
      pulse = result.split('@')[2]
      time = result.split('@')[3].split('.')[0]
      if float(sbp) > 140:
        highpressureTimes += 1
      elif float(dbp) > 90:
        highpressureTimes += 1
      elif float(sbp) < 90:
        lowpressureTimes += 1
      elif float(dbp) < 60:
        lowpressureTimes +=1
      
      dynamicContent.append(
        BoxComponent(
          layout='horizontal',
          margin='md',
          contents=[
            TextComponent(text=time[11:16], size='sm', color='#555555'),
            TextComponent(text=sbp+'/'+dbp, size='sm', color='#111111', align='end'),
            TextComponent(text=pulse, size='sm', color='#111111', align='end')
          ]
        )
      )   
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text='今日血壓', weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble, highpressureTimes, lowpressureTimes

def todayDiet(meal, resultList, day_text):
  
  calcSum = 0.0
  dynamicContent = [
    BoxComponent(
      layout='horizontal',
      contents=[
        TextComponent(text='名稱', weight='bold', size='sm', color='#555555'),
        TextComponent(text='千卡(kcal)', weight='bold', size='sm', color='#111111', align='end')
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if not resultList:
    pass
  else:
    for result in resultList:
      name = result.split('@')[0]
      cal = result.split('@')[1]
      calcSum += float(cal)
      dynamicContent.append(
        BoxComponent(
          layout='horizontal',
          margin='md',
          contents=[
            TextComponent(text=name, size='sm', color='#555555'),
            TextComponent(text=cal, size='sm', color='#111111', align='end')
          ]
        )
      )
    dynamicContent.append(SeparatorComponent(margin='md'))
  dynamicContent.append(
    BoxComponent(
      layout='horizontal',
      margin='md',
      contents=[
        TextComponent(text='total', size='sm', color='#555555'),
        TextComponent(text=str(calcSum), size='sm', color='#111111', align='end')
      ]
    )
  )
      
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text=day_text+meal, weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble

def todaySport(resultList):
  calcSum = 0.0
  totalTime = 0.0
  dynamicContent = [
    BoxComponent(
      layout='horizontal',
      contents=[
        TextComponent(text='名稱', weight='bold', size='sm', color='#555555'),
        TextComponent(text='時間(分鐘)', weight='bold', size='sm', color='#111111', align='end'),
        TextComponent(text='千卡(kcal)', weight='bold', size='sm', color='#111111', align='end')
      ]
    ),
    SeparatorComponent(margin='md')
  ]
  if not resultList:
    pass
  else:
    for result in resultList:
      name = result.split('@')[0]
      time = result.split('@')[1]
      cal = result.split('@')[2]
      roundCal = round(float(cal), 1)
      calcSum += float(cal)
      totalTime += float(time)
      dynamicContent.append(
        BoxComponent(
          layout='horizontal',
          margin='md',
          contents=[
            TextComponent(text=name, size='sm', color='#555555'),
            TextComponent(text=time, size='sm', color='#111111', align='end'),
            TextComponent(text=str(roundCal), size='sm', color='#111111', align='end')
          ]
        )
      )
    dynamicContent.append(SeparatorComponent(margin='md'))
    calcSum = round(calcSum, 1)
  dynamicContent.append(
    BoxComponent(
      layout='horizontal',
      margin='md',
      contents=[
        TextComponent(text='total', size='sm', color='#555555'),
        TextComponent(text=str(calcSum), size='sm', color='#111111', align='end')
      ]
    )
  )
      
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text='今日運動', weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble, totalTime

def queryRecord(event):
    user_id = event.source.user_id
    bubble = BubbleContainer(
    direction='ltr',
    body=BoxComponent(
        layout='vertical',
        spacing='sm',
        contents=[
            # title
            TextComponent(text='查詢記錄種類', weight='bold', size='xl'),
            SeparatorComponent(),
            TextComponent(text='飲食', weight='bold', size='xl'),
            BoxComponent(
                layout = 'vertical',
                spacing ='sm',
                contents=[
                    
                    #ButtonComponent(
                        #style='primary',
                        #height='sm',
                        #color='#239B56', #dark green
                        # action=PostbackAction(label='今日飲食', data='/today_diet')
                        #action=URIAction(label='今日飲食',uri=config.FOOD_RECORD_SEARCH_LIFF_URI)
                    #),
                   
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#2874A6', #dark blue
                        # action=PostbackAction(label='當週飲食', text='查詢當週飲食', data='/dietgraph')
                        action=URIAction(label='飲食日誌',uri='https://selab1.cs.nthu.edu.tw/food-record-web/'+user_id)
                    )
                ]
            ),
            SeparatorComponent(),
            TextComponent(text='運動', weight='bold', size='xl'),
            BoxComponent(
                layout = 'vertical',
                spacing ='sm',
                contents=[
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#239B56', #dark green
                        action=PostbackAction(label='今日運動', data='/today_sport')
                    ),
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#2874A6', #dark blue
                        action=PostbackAction(label='當週運動', text='查詢當週運動', data='/sportgraph')
                    )
                ]
            ),
            '''
            SeparatorComponent(),
            TextComponent(text='熱量', weight='bold', size='xl'),
            BoxComponent(
                layout = 'vertical',
                spacing ='sm',
                contents=[
                    ButtonComponent(
                      style='primary',
                      height='sm',
                      color='#2874A6', #dark blue
                      action=PostbackAction(label='當週熱量', text='查詢當週熱量', data='/caloriegraph')
                    )
                ]
            ),
            '''
            SeparatorComponent(),
            TextComponent(text='飲水量', weight='bold', size='xl'),
            BoxComponent(
                layout = 'vertical',
                spacing ='sm',
                contents=[
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#239B56', #dark green
                        action=PostbackAction(label='今日飲水量', data='/today_water')
                    ),
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#2874A6', #dark blue
                        action=PostbackAction(label='當週飲水量', text='查詢當週飲水量', data='/watergraph')
                    )
                ]
            ),
            SeparatorComponent(),
            TextComponent(text='血壓', weight='bold', size='xl'),
            BoxComponent(
                layout = 'vertical',
                spacing ='sm',
                contents=[
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#239B56', #dark green
                        action=PostbackAction(label='今日血壓', data='/today_BP')
                    ),
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#2874A6', #dark blue
                        action=PostbackAction(label='當週血壓', text='查詢當週血壓', data='/pressuregraph')
                    )
                ]
            ),
            SeparatorComponent(),
            TextComponent(text='體溫', weight='bold', size='xl'),
            BoxComponent(
                layout = 'vertical',
                spacing ='sm',
                contents=[
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#239B56', #dark green
                        action=PostbackAction(label='今日體溫', data='/today_temp')
                    ),
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        color='#2874A6', #dark blue
                        action=PostbackAction(label='當週體溫', text='查詢當週體溫', data='/tempgraph')
                    )
                ]
            ),

        ]
    )
  )
    return bubble

def recordOverview(userInfoList, userDiseaseList, userBPList, userTemperatureList, calorieSum, waterSum, sportTime):
  userGender = ''
  waterToDrink = 0
  energyNeed = 0
  BMR = 0
  standardWeight = 0
  BMI = dict()
  fatRate = dict()

  BMI['value'] = round(float(userInfoList['weight'])/((float(userInfoList['height'])/100)**2),1)

  # Set body fat rate
  if userInfoList['bodyFatRate'] is None:
    fatRate['value'] = "未設定"
  else:
    fatRate['value'] = float(userInfoList['bodyFatRate'])
  if DEBUG:
    print('fatRate["value"]: ', fatRate['value'])

  # Calculate daily water requirement by age
  if int(userInfoList['age']) < 30:
    waterToDrink = float(userInfoList['weight'])*40
  elif int(userInfoList['age']) >= 30 and int(userInfoList['age']) <= 55:
    waterToDrink = float(userInfoList['weight'])*35
  elif int(userInfoList['age']) > 55:
    waterToDrink = float(userInfoList['weight'])*30
  if DEBUG:
    print('userInfoList["age"]: ', int(userInfoList['age']))
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
  if userInfoList['gender']=='male':
    userGender = '男'
    if fatRate['value'] == "未設定":
      fatRate['level'] = "請設定體脂率"
      fatRate['color'] = GRAY
    elif int(userInfoList['age']) <= 30:
      if fatRate['value'] >= 20:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
    elif int(userInfoList['age']) > 30:
      if fatRate['value'] >= 25:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
  elif userInfoList['gender']=='female':
    userGender = '女'
    if fatRate['value'] == "未設定":
      fatRate['level'] = "請設定體脂率"
      fatRate['color'] = RED
    elif int(userInfoList['age']) <= 30:
      if fatRate['value'] >= 25:
        fatRate['level'] = '肥胖'
        fatRate['color'] = ORANGE
      else:
        fatRate['level'] = '標準'
        fatRate['color'] = GREEN
      fatRate['value'] = str(fatRate['value']) + ' %'
    elif int(userInfoList['age']) > 30:
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
  if userInfoList['gender']=='male':
    BMR = (13.7 * float(userInfoList['weight'])) + (5.0 * float(userInfoList['height'])) - (6.8 * float(userInfoList['age'])) + 66
  elif userInfoList['gender']=='female':
    BMR = (9.6 * float(userInfoList['weight'])) + (1.8 * float(userInfoList['height'])) - (4.7 * float(userInfoList['age'])) + 655
    
  if userInfoList['workLoad'] == '臥床躺著不動':
    energyNeed = BMR * 1.2
  elif userInfoList['workLoad'] == '輕度工作者':
    energyNeed = BMR * 1.375
  elif userInfoList['workLoad'] == '中度工作者':
    energyNeed = BMR * 1.55
  elif userInfoList['workLoad'] == '重度工作者':
    energyNeed = BMR * 1.725
  
  if DEBUG:
    print('workload: ', userInfoList['workLoad'])
    print('BMR: ', BMR)
    print('energyNeed: ', energyNeed)
  #===== end of calculate energy need per day ======

  #===== calculate standard weight =======
  if userInfoList['gender']=='male':
    standardWeight = (float(userInfoList['height']) - 170)*0.6 + 62
  elif userInfoList['gender']=='female':
    standardWeight = (float(userInfoList['height']) - 158)*0.5 + 52
  if DEBUG:
      print('standardWeight: ', standardWeight)
  #===== end of calculate standard weight =======



  #====== BP & temperature =======
  BPresult = userBPList[0]
  sbp = BPresult.split('@')[0]
  dbp = BPresult.split('@')[1]
  pulse = BPresult.split('@')[2]
  BP = sbp + '/' + dbp + '/' + pulse
  print(BP)

  tempresult = userTemperatureList[0]
  temperature = tempresult.split('@')[0] + ' ℃'
  print(temperature)




  #====== end of BP & temperature ======


  if DEBUG:
    print("before dynamicContent")

  dynamicContent = [
    BoxComponent(
      layout='vertical',
      spacing='md',
      contents=[
        TextComponent(text='健康總覽', weight='bold',size='lg', color=GREEN, align='center'),
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
            TextComponent(text=userInfoList['age']+' 歲', weight='bold', size='sm', color=GRAY, align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='身高', weight='bold', size='sm', color=BLACK),
            TextComponent(text=userInfoList['height']+' 公分', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='體重', weight='bold', size='sm', color=BLACK),
            TextComponent(text=userInfoList['weight']+' 公斤', weight='bold', size='sm', color=GRAY, align='start')
          ],
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='建議之標準體重', weight='bold', size='xs', color=BLACK),
            TextComponent(text= str(int(standardWeight)) +' 公斤', weight='bold', size='xs', color=GRAY, align='start')
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
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='收縮壓/舒張壓/脈搏', weight='bold', size='xs', color=BLACK),
            TextComponent(text= BP, weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='體溫', weight='bold', size='sm', color=BLACK),
            TextComponent(text= temperature, weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='今日總攝取熱量', weight='bold', size='sm', color=BLACK),
            TextComponent(text= str(int(calorieSum)) + ' 大卡', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='每日建議攝取熱量', weight='bold', size='xs', color=BLACK),
            TextComponent(text= str(int(energyNeed)) +' 大卡', weight='bold', size='xs', color=GRAY, align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='今日總飲水量', weight='bold', size='sm', color=BLACK),
            TextComponent(text= str(int(waterSum)) + ' ml', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='每日建議飲水量', weight='bold', size='xs', color=BLACK),
            TextComponent(text= str(int(waterToDrink)) +' ml', weight='bold', size='xs', color=GRAY, align='start')
          ],
        ),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='今日運動總時間', weight='bold', size='sm', color=BLACK),
            TextComponent(text= str(int(sportTime)) + ' 分鐘', weight='bold', size='sm', color=GRAY,  align='start')
          ],
        ),
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
    print("before carousel")
  carousel = CarouselContainer(
    contents=[bubble]
  )
  return carousel
# end of healthInfo


def iBeacon_template():
  dynamicContent = [
    BoxComponent(
      layout='vertical',
      spacing='md',
      contents=[
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='藍莓蛋糕', weight='bold', size='md', color='#555555'),
            TextComponent(text='$60/塊', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='採用進口智利產高級藍莓，享受幸福新滋味', weight='bold', size='xs', color='#555555'),
          ]
        ),
        ImageComponent(url='https://i.imgur.com/85kVhS8.jpg',margin='none',align='start',size='4xl'),
        SeparatorComponent(margin='sm')
      ] 
    )
  ]

  dynamicContent.append(
    BoxComponent(
      layout='vertical',
      spacing='md',
      contents=[
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='檸檬千層派', weight='bold', size='md', color='#555555'),
            TextComponent(text='$80/塊', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='酸甜檸檬配上酥軟派層，下午茶首選', weight='bold', size='xs', color='#555555'),
          ]
        ),
        ImageComponent(url='https://i.imgur.com/p8S1q6a.jpg',margin='none',align='start',size='4xl'),
        SeparatorComponent(margin='md')
      ] 
    )
  )
      
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text='水木蛋糕店 春季優惠', weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble


def nutrition_template():
  dynamicContent = [
    BoxComponent(
      layout='vertical',
      spacing='md',
      contents=[
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='每一份量', weight='bold', size='md', color='#555555'),
            TextComponent(text='19.5公克', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        SeparatorComponent(margin='sm'),
        TextComponent(text='每份', weight='bold', size='md', color='#555555',align='end'),
        SeparatorComponent(margin='sm'),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='熱量', weight='bold', size='md', color='#555555'),
            TextComponent(text='89大卡', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='蛋白質', weight='bold', size='md', color='#555555'),
            TextComponent(text='2.5公克', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='脂肪', weight='bold', size='md', color='#555555'),
            TextComponent(text='1.2公克', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='碳水化合物', weight='bold', size='md', color='#555555'),
            TextComponent(text='17公克', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
        BoxComponent(
          layout='horizontal',
          contents=[
            TextComponent(text='鈉', weight='bold', size='md', color='#555555'),
            TextComponent(text='116毫克', weight='bold', size='md', color='#111111', align='end')
          ]
        ),
      ] 
    )
  ]

      
  bubble = BubbleContainer(
    direction='ltr',
    header = BoxComponent(
      layout='vertical',
      spacing='sm',
      contents=[
        TextComponent(text='法式熱壓吐司佐野莓果醬', weight='bold', size='xl', margin='md')
      ]
    ),
    body=BoxComponent(
      layout='vertical',
      contents=dynamicContent
    )
  )
  return bubble

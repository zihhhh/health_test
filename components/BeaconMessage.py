from linebot.models import *

class BeaconMessage():
    def __init__(self):
        pass

    def buildComponent(self):
        return BubbleContainer(
            direction = 'ltr',
            body = BoxComponent(
                layout = 'vertical',
                contents = [BoxComponent(
                    layout = 'vertical',
                    contents = [
                        TextComponent(text='附近飲食推薦', weight='bold', size='xl'),
                        TextComponent(text='以下是為你推薦附近的午餐菜單', weight='bold', size='xs', color='#555555'),
                        TextComponent(text='點擊即可新增飲食紀錄', weight='bold', size='xs', color='#555555')
                    ]
                ),
                BoxComponent(
                    layout='vertical',spacing='xs',margin='xl',
                    contents=[
                        BoxComponent(
                            layout='horizontal',
                            contents=[
                                TextComponent(text='皿富器食 minfood 花雕野菜', weight='bold', size='md', color='#555555', flex=0),
                                TextComponent(text='$' + str(255), weight='bold', size='md', color='#111111', align='end')
                            ]
                        ),
                        TextComponent(text='餐點熱量為' + str(340) + '大卡', weight='bold', size='xs', color='#555555'),
                        ImageComponent(url='https://i.imgur.com/376iFbj.jpg', margin='none',align='center',size='4xl')
                    ]
                )
                ]
            )
        )
    
    def showPath(self, recommendPath):
        comp = []
        comp.append(
            BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text=recommendPath['startName'], weight='bold', size='lg', color='#111111', flex=0),
                    TextComponent(text=' ' + '往'+' ', weight='bold', size='md', color='#555555', flex=0)
                ]
            )
        )
        comp.append(TextComponent(text=recommendPath['end_name'], weight='bold', size='lg', color='#111111', flex=0, align='end'))
        '''
        comp.append(
            BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text=str(recommendPath['start_position']), weight='bold', size='md', color='#555555'),
                    TextComponent(text=str(recommendPath['end_position']), weight='bold', size='md', color='#555555', align='end')
                ]
            )
        )
        '''
        comp.append(TextComponent(text='路線總長:'+str(recommendPath['length'])+'公尺', weight='bold', size='md', color="#a52a2a", align='end'))
            

        bubble = BubbleContainer(
            direction = 'ltr',
            body = BoxComponent(
                layout = 'vertical',
                contents = [BoxComponent(
                    layout = 'vertical',
                    contents = [
                        TextComponent(text='推薦路線', weight='bold', size='xl', color='#696969')
                    ]
                ),
                BoxComponent(
                    layout='vertical',spacing='md',margin='xl',
                    contents=comp
                ),
                ButtonComponent(
                    action=URIAction(label="開啟google看詳細資訊", uri=recommendPath['web']),
                    style='secondary', color="#87cefa"
                )
                ]
            )
        )
        return bubble



    def showList(self, recommendList):
        comp = []
        for item in recommendList:
            comp.append(TextComponent(text=item['shopName'], weight='bold', size='lg', color='#000000', flex=0))
            comp.append(
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text=' ' + '推薦'+' ', weight='bold', size='xs', color='#ffa500', flex=0),
                        TextComponent(text=item['mealName'], weight='bold', size='lg', color='#2f4f4f', flex=0),
                        TextComponent(text='$' + str(item['price']), weight='bold', size='md', color='#111111', align='end')
                    ]
                )
            )
            comp.append(
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text='餐點熱量為 ', weight='bold', size='xs', color='#111111', flex=0),
                        TextComponent(text=str(item['kcal']) + '大卡', weight='bold', size='md', color='#cd5c5c', flex=0)
                    ]
                )
            )
            comp.append(ImageComponent(url=item['picture'], margin='none',align='center',size='4xl'))
            comp.append(TextComponent(text=' ', size='md'))

        bubble = BubbleContainer(
            direction = 'ltr',
            body = BoxComponent(
                layout = 'vertical',
                contents = [BoxComponent(
                    layout = 'vertical',
                    contents = [
                        TextComponent(text='附近餐點推薦', weight='bold', size='xl', color='#696969')
                    ]
                ),
                BoxComponent(
                    layout='vertical',spacing='md',margin='xl',
                    contents=comp
                )
                ]
            )
        )
        return bubble
    
    def nearbyFood(self, recommendList):
        bubble = []
        for item in recommendList:
            comp = []
            comp.append(TextComponent(text=item['shopName'], weight='bold', size='lg', color='#000000', flex=0))
            comp.append(
                BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text=' ' + '推薦'+' ', weight='bold', size='xs', color='#ffa500', flex=0),
                        TextComponent(text=item['mealName'], weight='bold', size='lg', color='#2f4f4f', flex=0),
                        TextComponent(text='$' + str(item['price']), weight='bold', size='md', color='#111111', align='end')
                    ]
                )
            )
            comp.append(
                    BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text='餐點熱量為 ', weight='bold', size='xs', color='#111111', flex=0),
                        TextComponent(text=str(item['kcal']) + '大卡', weight='bold', size='md', color='#cd5c5c', flex=0)
                    ]
                )
            )
            comp.append(ImageComponent(url=item['picture'], margin='none',align='center',size='4xl'))
            comp.append(TextComponent(text=' ', size='md'))
            bubble.append(BubbleContainer(
                direction='ltr',
                body = BoxComponent(
                    layout='vertical',
                    contents=comp
                )
            ))

        carousel = CarouselContainer(bubble)
        return carousel

from linebot.models import *
import config

class EatAdvice():
    def __init__(self, shopName, foodName, calorie, price, imageUrl):
        self.shopName = shopName
        self.foodName = foodName
        self.calorie = calorie
        self.price = price
        self.imageUrl = imageUrl

class EatAdviceMessage():
    def __init__(self, totalCalorie):
        self._contentComponents = []
        self._contentComponents.append(
            BoxComponent(
                layout='vertical',
                contents= [
                    TextComponent(text='飲食建議', weight='bold', size='xl'),
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text='今天已攝取的熱量為 ', weight='bold', flex=0, size='xs', color='#555555'),
                            TextComponent(text=str(totalCalorie), weight='bold', flex=0, size='xs', color='#ff0000'),
                            TextComponent(text=' 大卡', weight='bold', size='xs', flex=0, color='#555555')
                        ]
                    ),
                    TextComponent(text='以下是為你推薦附近的午餐菜單', weight='bold', size='xs', color='#555555'),
                    TextComponent(text='點擊即可新增飲食紀錄', weight='bold', size='xs', color='#555555')
                ]
            )
        )
    
    def addAdvice(self, eatAdvice):
        if (not type(eatAdvice) == EatAdvice):
            return 
        self._contentComponents.append(            
            BoxComponent(
                layout='vertical',spacing='xs',margin='xl',
                contents=[
                    BoxComponent(
                        layout='horizontal',
                        contents=[
                            TextComponent(text=eatAdvice.shopName + ' ' + eatAdvice.foodName, weight='bold', size='md', color='#555555', flex=0),
                            TextComponent(text='$' + str(eatAdvice.price), weight='bold', size='md', color='#111111', align='end')
                        ]
                    ),
                    TextComponent(text='餐點熱量為' + str(eatAdvice.calorie) + '大卡', weight='bold', size='xs', color='#555555'),
                    ImageComponent(url=eatAdvice.imageUrl, margin='none',align='center',size='4xl')
                ]
            )
        )

    def buildComponent(self):
        self._contentComponents.append(
            ButtonComponent(
                style='link',
                height='sm',
                action=URIAction(label='點此查看其他附近餐點',uri=config.RESTAURANT_LIFF_URI),
            )
        )
        return BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=self._contentComponents
            )
        )
from linebot.models import PostbackAction, ButtonsTemplate, TemplateSendMessage, TextSendMessage
from LineInitializer import line_bot_api, handler
import constant

class EatIntroduceController():
    def __init__(self):
        pass
    
    @staticmethod
    def ketogenicDiet(event):
        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlLogo, title='生酮飲食',text='Ketogenic diet',actions=[
            PostbackAction(label='介紹',data='/ketoA'),
            PostbackAction(label='推薦食物',data='/ketoB'),
            PostbackAction(label='禁忌食物',data='/ketoC')])
        template_message = TemplateSendMessage(alt_text='Buttons alt text',template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    @staticmethod
    def ketoA(event):
        text_message1 = TextSendMessage(text='生酮飲食的特色在於低量碳水化合物的攝取(一天最多20克)，'+
                                        '使得身體必須燃燒自身脂肪產生酮體以提供足夠的熱量，能夠達到快速減重的效果')
        text_message2 = TextSendMessage(text='然而生酮飲食的熱量來源主要來自脂肪，攝取大量的脂肪會提升罹患心血管疾病的風險，且酮體代謝後'+
                                        '會產生酮酸，酮酸過多會導致酮酸中毒，對於心臟病、糖尿病患者來說可能會導致病情惡化，因此不建議兩者病患採行此方法')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def ketoB(event):
        text_message1 = TextSendMessage(text='主要為各式脂肪來源(肉類、植物油)和蔬菜，同時需要大量飲水(緩和酮酸濃度及避免身體缺水)')
        text_message2 = TextSendMessage(text='肉類、全脂鮮奶、奶油、蔬菜、植物油、堅果類')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def ketoC(event):
        text_message1 = TextSendMessage(text='碳水化合物一定要少，因此高澱粉、高糖分食物盡可能不要吃')
        text_message2 = TextSendMessage(text='五穀根莖類、水果、豆類、甜食、酒精、裹麵衣的油炸食物')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def muscleDiet(event):
        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlLogo,title='健身',text='Muscle build',actions=[
            PostbackAction(label='介紹',data='/muscleA'),
            PostbackAction(label='推薦食物',data='/muscleB'),
            PostbackAction(label='禁忌食物',data='/muscleC')])
        template_message = TemplateSendMessage(alt_text='Buttons alt text',template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    @staticmethod
    def muscleA(event):
        text_message1 = TextSendMessage(text='健身的目的在於提升肌肉量、減少體脂肪，能提升身體機能'+
                                        '雕塑體態，肌肉來源於蛋白質，因此健身者需要大量獲取蛋白質並減少醣類的攝取以避免增加體脂率')
        text_message2 = TextSendMessage(text='雖然醣類、脂肪會影響體脂，但如果不是想要走健美路線的話'+
                                        '不一定要盡量避免，減量即可，例如可用水煮、清蒸等方式烹調食物'+
                                        '主食以馬鈴薯、糙米、全麥等取代白飯，可以減少脂肪和醣類的攝取')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def muscleB(event):
        text_message1 = TextSendMessage(text='各種肉類(瘦肉，牛、雞為佳)、乳清蛋白、黃豆類、雞蛋(蛋白為佳)')
        line_bot_api.reply_message(event.reply_token, text_message1)

    @staticmethod
    def muscleC(event):
        text_message1 = TextSendMessage(text='澱粉、脂肪減量或不吃')
        text_message2 = TextSendMessage(text='白飯、油炸食物、甜食')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def dashDiet(event):
        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlLogo,
                                    title='得舒飲食',text='Dash',actions=[
                                    PostbackAction(label='介紹',data='/dashA'),
                                    PostbackAction(label='推薦食物',data='/dashB'),
                                    PostbackAction(label='禁忌食物',data='/dashC')])
        template_message = TemplateSendMessage(alt_text='Buttons alt text',
                                        template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    @staticmethod
    def dashA(event):
        text_message1 = TextSendMessage(text='得舒飲食是為了防止高血壓而發展出來的飲食法，'+
                                        '減少納、油脂的攝取，提升其他的礦物質和膳食纖維的攝取，'+
                                        '有助於降低血壓，得舒飲食原則上鼓勵吃素，但不用只吃素')
        text_message2 = TextSendMessage(text='得舒飲食以蔬果、全榖、瘦肉、低脂乳品為主，尤其蔬果比例'+
                                        '需要足夠，根據身體當前體重和活動量來決定一天的熱量攝取，'+
                                        '過輕者約40x體重，正常者約35x體重，過重者約30x體重')
        text_message3 = TextSendMessage(text='對於糖尿病、腎臟病患者需注意，因為得舒注重蔬果的攝取，'+
                                        '糖尿病患者要小心水果帶來的血糖飆升，腎臟病患者要小心豐富礦物質對'+
                                        '腎臟的負擔，患者需要先諮詢醫生再決定如何吃較佳')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2,text_message3])

    @staticmethod
    def dashB(event):
        text_message1 = TextSendMessage(text='全穀類、蔬果、低脂乳製品、黃豆類')
        line_bot_api.reply_message(event.reply_token, text_message1)

    @staticmethod
    def dashC(event):
        text_message1 = TextSendMessage(text='少量即可，不需全禁')
        text_message2 = TextSendMessage(text='肉類、脂肪類、甜食(可選擇少油或水果代替)')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def glutenfreeDiet(event):
        buttons_template = ButtonsTemplate(thumbnail_image_url=constant.imageUrlLogo,title='無麩質飲食',text='Gluten free',actions=[
            PostbackAction(label='介紹',data='/glutenA'),
            PostbackAction(label='推薦食物',data='/glutenB'),
            PostbackAction(label='禁忌食物',data='/glutenC')])
        template_message = TemplateSendMessage(alt_text='Buttons alt text',
                                        template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    @staticmethod
    def glutenA(event):
        text_message1 = TextSendMessage(text='麩質，又稱麵筋(蛋白)，存在於許多穀物中的一種蛋白質，'+
                                        '尤其麥類的含量特別多，然而此種蛋白無法被人類完全分解，'+
                                        '有些人會對麩質分解後的產物產生過敏')
        text_message2 = TextSendMessage(text='麩質過敏症狀有很多，如腸胃不適，嚴重者會拉肚子和腸道發炎'+
                                        '(乳糜瀉)，或是皮膚癢、起疹、喉嚨痛等典型過敏反應，'+
                                        '因此為了這些對麩質過敏的患者，無麩質飲食便誕生了，特色自然就是'+
                                        '避免攝取任何麩質(症狀輕微的可以少量攝取)')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def glutenB(event):
        text_message1 = TextSendMessage(text='原則上只有避免攝取麩質，推薦以米類或其他根莖類食物取代麥類')
        text_message2 = TextSendMessage(text='糙米、馬鈴薯、玉米、堅果類、豆類')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2])

    @staticmethod
    def glutenC(event):
        text_message1 = TextSendMessage(text='含麩質食物皆不要吃')
        text_message2 = TextSendMessage(text='麥類及其製品(麵包、麵條、麵粉)')
        text_message3 = TextSendMessage(text='另外需注意雜糧米、薏仁等產品，有的雜糧米會混有麥類而因大麥又稱小薏仁(或洋薏仁)，可能會有混淆之餘')
        line_bot_api.reply_message(event.reply_token, [text_message1,text_message2,text_message3])
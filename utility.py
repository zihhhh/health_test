from linebot.models import TextSendMessage
import operator
import requests
import json
from datetime import datetime
import config
import csv
import json

# Useless function
def TextAnalysis(text=''):
    disease = [1,0,1,0] # this line is temporarily added
    advise = '該菜單可能包含不宜多吃的食物:\n'
    abandon = []
    heart = ['炸', '牛', '豬', '羊', '薯條', '雞塊', '雞排', '酒', '辣', '香腸', '火腿'] # the keywords of abandoned food, except: '甜不辣', '牛角', '牛奶', '羊奶'
    diabete = ['米','飯','麵','麥','薯','地瓜','芋頭','薏仁','粥','吐司','可頌', # the keywords of abandoned food
             '餃','鍋貼','南瓜','冬粉','螞蟻上樹','饅頭','包','燒賣','油條', '堡', '派',
             '蔥油餅','蛋餅','貝果','三明治', '泡芙', '巧克力', '冰淇淋', '奶茶', '奶昔', '汽水', '可樂', '蘇打', '餅']
    bloodPressure = ['牛', '豬', '羊', '堡', '貢丸', '魚丸', '醬', '麵包', '餅乾', '蛋糕', '麵', '腰子', '雞皮', # the keywords of abandoned food, except: '甜不辣', '牛角', '牛奶', '羊奶'
             '鴨皮', '燻雞', '榨菜', '酸菜', '醬菜', '梅乾菜', '蜜餞', '肉鬆', '魚鬆', '火腿', '豆瓣', '辣椒', '沙茶',
             '豆腐乳', '肉醬', '奶油', '火鍋']
    belly = ['湯', '茶泡飯', '蕎麥', '醋', '生魚片', '生菜', '生雞蛋', '竹筍', '牛蒡', '南瓜', '芥菜', '蒟蒻', '海帶', '紫菜',
             '海苔', '藻', '柑', '橘', '椪', '橙', '草莓', '鳳梨', '檸', '檬', '番茄醬', '茄汁']

    for food in text.split('\n'):
        print(food)
        if disease[0] == 1: # diabete
            for f in diabete:
                if food.find(f) >= 0:
                    abandon.append(f)
                    break
        if disease[1] == 1: # heart
            for f in heart:
                if food.find(f) >= 0:
                    abandon.append(f)
                    break
        if disease[2] == 1: # blood pressure
            for f in bloodPressure:
                if food.find(f) >= 0:
                    abandon.append(f)
                    break
        if disease[3] == 1: # belly
            for f in belly:
                if food.find(f) >= 0:
                    abandon.append(f)
                    break

    abandon_set = set(abandon)
    if len(abandon_set) > 0: advise = advise + '\n'.join(list(abandon_set))
    return advise

def order(data):
    food = data.split(' ')
    answer = dict()
    veg = ['菜','番茄','茄子','茼蒿','冬瓜','苦瓜','青椒','沙拉','蘿蔔','菜頭',
           '筍','豆苗','豆芽','苜蓿','四季豆','豌豆']
    meat = ['肉','豬','蛋','雞','牛','羊','鴨','鵝','魚','蝦','貝',
            '透抽','小卷','中卷','小管','魷魚','章魚','蛤蜊','牡蠣',
            '黃豆','黑豆','豆漿','紅豆','綠豆','豆腐','豆皮','排骨',
            '肝連','火腿','培根','香腸','大腸','小腸']
    fat = ['牛奶','羊奶','奶油','黃油','牛油','豬油','橄欖油','麻油','葵花油',
           '花生','焗烤','開心果','杏仁','腰果','芝麻','扁桃仁','乳','胡桃',
           '核桃','榛果','栗','堅果','葵花籽','南瓜籽','酪梨']
    grain = ['米','飯','麵','麥','薯','地瓜','芋頭','薏仁','粥','吐司','可頌',
             '餃','鍋貼','南瓜','冬粉','螞蟻上樹','饅頭','包','燒賣','油條',
             '蔥油餅','抓餅','蛋餅','貝果','三明治','堡', '派']
    fruit = ['莓','橘','柑','蘋','葡萄','蕉','龍眼','芭樂','木瓜','西瓜',
             '蓮霧','梨','李','桃子','柿','榴槤','石榴','荔枝','枸杞','萊姆',
             '檸','檬','橙','柚','文旦','杏子','水蜜桃','百香果','無花果',
             '火龍果']
    for f in food:
        tmp = f
        score = 0
        
        if f in veg: score = 5
        elif f in meat: score = 4
        elif f in fat: score = 3
        elif f in grain: score = 2
        elif f in fruit: score = 1
        else:
            for v in veg:
                if tmp.find(v) >= 0:
                    score = 5
                    tmp = tmp.replace(v, '')
                    break
            for fa in fat:
                if tmp.find(fa) >= 0:
                    if score > 0:
                        score = score - 0.5
                    else:
                        score = 3
                    tmp = tmp.replace(fa, '')
                    break
                
            for m in meat:
                if tmp.find('蛋糕') >= 0 or tmp.find('蛋捲') >= 0 or tmp.find('蛋塔') >= 0:
                    if score > 0:
                        score = score - 4
                    else:
                        score = -3
                    break
                if tmp.find(m) >= 0:
                    if score < 5 and score > 0:
                        score = score + 0.2
                    elif score == 5:
                        score = score - 0.5
                    else:
                        score = 4
                    tmp = tmp.replace(m, '')
                    break
            for g in grain:
                if score < 0:
                    break
                if tmp.find(g) >= 0:
                    if score > 0:
                        score = score - 2.5
                    else:
                        score = 2
                    tmp = tmp.replace(g, '')
                    break
            for fr in fruit:
                if score < 0:
                    break
                if tmp.find(fr) >= 0:
                    if score > 0:
                        score = score - 3.5
                    else:
                        score = 1
                    break
        
        if score == 0:
            score = -3
        
        print(f+' '+str(score))
        answer[f] = score
    return sorted(answer.items(), key=operator.itemgetter(1), reverse=True)

def foodConflict(foods):
    column = []
    with open('FoodConflictList.csv', 'r', encoding = "utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            column.append(row)
    # print(column)
    table = json.loads(json.dumps(column))
    conflictMsg = []
    
    for row in table:
        flag1 = 0
        flag2 = 0
        for food in foods:
            if row['food1'] == food:
                flag1 +=1
            elif row['food2'] == food:
                flag2 +=1
            else:
                for i in range(len(food)):
                    temp1 = food[i:i+len(row['food1'])]
                    temp2 = food[i:i+len(row['food2'])] 
                    if row['food1'] == temp1:
                        flag1 +=1
                        break
                    elif row['food2'] == temp2:
                        flag2 +=1
                        break
        if flag1 != 0 and flag2 != 0:
            conflictMsg.append(row)
        
    return conflictMsg

def diseaseFood(foods, disease, file_name):

    column = []
    with open(file_name, 'r', encoding = "utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            column.append(row)
    # print(column)
    diseaseTable = json.loads(json.dumps(column))

    diseaseMsg = []

    for food in foods:
        flag = 0
        for row in diseaseTable:
            if int(row['disease']) == disease:
                if flag == 0:
                    if row['food'] == food:
                        diseaseMsg.append(food + ' ')
                        flag = 1
                        break
                    else:
                        for i in range(len(food)):
                            temp = food[i:i+len(row['food'])]
                            if row['food'] == temp:
                                diseaseMsg.append(food + ' ')
                                flag = 1
                                break
                else:
                    break

    return diseaseMsg

def foodDictionary(food):
    Dictionary = {'牛':'牛肉', '豬':'豬肉','羊':'羊肉', '肝':'動物肝臟', '奶':'牛奶', '豆':'豆類', '蛋':'雞蛋', '蟹':'螃蟹', '梨':'梨子', '橘':'柑橘類', '筍':'竹筍'}
    if Dictionary.__contains__(food):
        print(Dictionary[food])
        return Dictionary[food]
    else:
        return food

def foodsMessage(conflictMsg):
    msg = ''
    num = 1
    for item in conflictMsg:
        msg = msg+ '\n' + str(num) +'. ' + '「' + foodDictionary(item['food1']) + '」' + '和' + '「' + foodDictionary(item['food2']) + '」' + '衝突\n\t' + item['warning']
        num+=1
    return msg

def suggestMessage(diseaseMsg, medicineMsg, disease):
    disease_name = ['糖尿病', '心臟病', '高血壓', '肥胖']
    disease_text = ['含糖食物、高膽固醇食物等', '高脂肪/高膽固醇食物，且需少鈉', '肉類及醃製品等，或高脂肪/高膽固醇食物', '檸檬、柑橘、草莓、生食等']
    medicine_text = ['若有使用胰島素，應避免空腹飲酒', '若有服用心律不整、降血脂藥品，應避免同時攝食高纖食品', '若有服用降血壓藥，應避免同時攝食高鈉、高鉀食物', ' ']
    msg =   '「' + disease_name[disease] + '」'
    if len(diseaseMsg) != 0:
        msg = msg + '不宜多吃' + disease_text[disease] + '，如餐點中:'
        for item in diseaseMsg:
            msg = msg + ' ' + item
    if len(diseaseMsg) != 0 and len(medicineMsg) != 0:
        msg = msg + '\n'
    if len(medicineMsg) != 0:
        msg = msg + medicine_text[disease] + '，如餐點中:'
        for item in medicineMsg:
            msg = msg + ' ' + item
    return msg


def FoodRecordRecommend(userID, foodname):
    # Step1. 從資料庫拿疾病資訊
    getDisease = {
        'lineID' : userID,
    }
    response = requests.post(config.PHP_SERVER + 'mhealth/disease/queryUserDisease.php', data=getDisease)
    userDiseaseList = json.loads(response.text) #print(userDiseaseList)
    
    # Step2. 從資料庫撈今日累積熱量、累積成分
    param = {
        'queryRecordAll': 'queryRecordAll',
        'userID': userID,
        'queryTime': datetime.now()
    }
    response = requests.post(config.PHP_SERVER + 'mhealth/food/queryFoodRecord.php', data=param)
    resultList = json.loads(response.text)
    currentCal = 0.0
    currentFat = 0.0
    currentSugar = 0.0
    currentFiber = 0.0
    for result in resultList:
        # "name carolie fat sugar fiber"
        currentCal += float(result.split('@')[1])
        currentFat += float(result.split('@')[2])
        currentSugar += float(result.split('@')[3])
        currentFiber += float(result.split('@')[4])

    # Step3. 從疾病資料庫撈忌吃元素、建議吃元素、忌吃食物 
    rec1 = ""
    rec2 = ""
    for row in userDiseaseList:
        data = {
            'disease':row['disease']
        }
        response = requests.post(config.PHP_SERVER+'mhealth/disease/queryDiseaseDict.php', data=data)
        diseaseInfo = json.loads(response.text)
        #print(diseaseInfo)

        # 食物的忌吃元素熱量
        if diseaseInfo[0]['NotEat'] is not None:
            notEatToken = diseaseInfo[0]['NotEat'].split()
            for t in notEatToken:
                category = t.split('@')[0]
                percent = float(t.split('@')[1])
                #print(currentCal*percent/100)
                if category == 'fat':
                    if((currentFat*9) > (currentCal*percent/100)):
                        rec1 += "您患有"+diseaseInfo[0]['disease']+"，累積油脂已超過建議比例，請注意。\n"
                elif category == 'sugar':
                    if((currentSugar*4) > (currentCal*percent/100)):
                        rec1 += "您患有"+diseaseInfo[0]['disease']+"，累積糖分已超過建議比例，請注意。\n"
                elif category == 'fiber':
                    if((currentFiber*4) > (currentCal*percent/100)):
                        rec1 += "您患有"+diseaseInfo[0]['disease']+"，累積膳食纖維已超過建議比例，請注意。\n"
        
        # 食物的名稱含「忌吃食物」名稱
        if diseaseInfo[0]['NotEatFood'] is not None and foodname is not None:
            if foodname in diseaseInfo[0]['NotEatFood']:
                rec2 += "因您患有"+diseaseInfo[0]['disease']+"，不適合吃: "+diseaseInfo[0]['NotEatFood']+"\n" 
    allMessage = []
    if rec1 != "":
        allMessage.append(TextSendMessage(text=rec1))
    if rec2 != "":
        allMessage.append(TextSendMessage(text=rec2))
    return allMessage
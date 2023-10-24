import requests
import json
import config

class UserNotFoundError(Exception):
    pass

class User():
    def __init__(self, lineID, name, weight, height, age, gender, language, eatingHabit, bodyFatRate, workLoad):
        self.lineID = lineID
        self.name = name
        self.weight = weight
        self.height = height
        self.age = age
        self.gender = gender
        self.language = language
        self.eatingHabit = eatingHabit
        self.bodyFatRate = bodyFatRate
        self.workLoad = workLoad

    @staticmethod
    def isUserIDExist(lineID):
        isExist = False
        response = requests.post(config.PHP_SERVER + 'mhealth/lineUser/queryUserInfo.php')
        resultList = json.loads(response.text)
        for row in resultList:
            if (row['lineID'] == lineID):
                isExist = True
                break
        return isExist

    @staticmethod
    def add(lineID, name):
        requests.post(config.PHP_SERVER + 'mhealth/lineUser/createUser.php', data={
            'lineID': lineID,
            'name' : name
        })

    @staticmethod
    def getUserByLineID(lineID):
        response = requests.post(config.PHP_SERVER + 'mhealth/lineUser/queryUserInfo.php')
        resultList = json.loads(response.text)
        for row in resultList:
            if (row['lineID'] == lineID):
                lineID = row['lineID']
                name = row['name']
                weight = float(row['weight'] or 0)
                height = float(row['height'] or 0)
                age = int(row['age'] or 0)
                gender = row['gender']
                language = int(row['language'] or 0)
                eatingHabit = row['eatingHabit']
                bodyFatRate = float(row['bodyFatRate'] or 0)
                workLoad = row['workLoad']
                return User(lineID, name, weight, height, age, gender, language, eatingHabit, bodyFatRate, workLoad)
        raise UserNotFoundError
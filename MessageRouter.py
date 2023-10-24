import re

class MessageRouter():
    def __init__(self, routerType='text'):
        self._messageRouterMapping = {}
        self._routerType = routerType

    def findFuncRegex(self, message):
        for regPattern in self._messageRouterMapping:
            if re.match(regPattern, message):
                return self._messageRouterMapping[regPattern]
        return None

    def add(self, message, func):
        self._messageRouterMapping[message] = func

    def route(self, event):
        if (self._routerType == 'text'):
            func = self.findFuncRegex(event.message.text)
        elif (self._routerType == 'postback'):
            func = self.findFuncRegex(event.postback.data)
        if (func != None):
            func(event)
        return func != None
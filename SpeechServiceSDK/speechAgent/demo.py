# -*- encoding: UTF-8 -*-

""" 这是一个调用SpeechService服务接口获取语音识别和语义理解内容的示例

"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

NAO_IP = "192.168.1.106"


# Global variable to store the SpeechMoule instance
SpeechInstance = None
memory = None


class SpeechMoule(ALModule):

    #初始化
    def __init__(self, name):
        ALModule.__init__(self, name)
    
        self.tts = ALProxy("ALTextToSpeech")

        global memory
        memory = ALProxy("ALMemory")

        #开始识别
        memory.raiseEvent("GLOABALSTATE",1)

        #订阅语音识别和语义理解事件
        memory.subscribeToEvent("SpeechResult",
            "SpeechInstance",
            "onSpeechResult")

        #订阅识别超时事件
        memory.subscribeToEvent("TimeOut",
            "SpeechInstance",
            "onTimeOut")
        
        #订阅云端返回错误事件
        memory.subscribeToEvent("ErrorEvent",
            "SpeechInstance",
            "onErrorEventHandle")

        #订阅头部中间按键监听事件
        memory.subscribeToEvent("MiddleTactilTouched",
            "SpeechInstance",
            "onMiddleHeadTouched")
        
        #订阅头后部按键监听事件
        memory.subscribeToEvent("RearTactilTouched",
            "SpeechInstance",
            "onRearHeadTouched")

    #头部中间按钮触摸事件，机器人停止合成并开始识别
    def onMiddleHeadTouched(self, *_args):
        self.tts.stopAll()
        memory.raiseEvent("GLOABALSTATE",1)

    #头部后部按钮触摸事件，机器人停止合成并不再识别
    def onRearHeadTouched(self, *_args):
        self.tts.stopAll()
        memory.raiseEvent("GLOABALSTATE",0)

    #获取云端返回错误码
    def onErrorEventHandle(self, *_args):
        errorCode = memory.getData("ErrorEvent")
        print errorCode
            
    def onSpeechResult(self, *_args):
        
        """ 每当语音识别结果返回时触发该函数
        """
        memory.raiseEvent("GLOABALSTATE",0)
        result = memory.getData("SpeechResult")
        print result

        memory.unsubscribeToEvent("SpeechResult",
            "HumanGreeter")
        
        self.tts.say(result)

        memory.raiseEvent("GLOABALSTATE",1)

        # Subscribe again to the event
        memory.subscribeToEvent("SpeechResult",
            "SpeechInstance",
            "onSpeechResult")
        
    def onTimeOut(self, *_args):
        memory.unsubscribeToEvent("TimeOut",
            "SpeechInstance")

        memory.raiseEvent("GLOABALSTATE",0)
        
        self.tts.say("没听清")

        memory.raiseEvent("GLOABALSTATE",1)
         
        memory.subscribeToEvent("TimeOut",
            "SpeechInstance",
            "onTimeOut")


def main():
    """ Main entry point

    """
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SpeechInstance
    SpeechInstance = SpeechMoule("SpeechInstance")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()




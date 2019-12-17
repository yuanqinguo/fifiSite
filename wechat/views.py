# coding:utf-8

import hashlib
import random
import time
import requests
import json
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

#媒体ID存储
Image_Mediaid_List = []
Voice_Mediaid_List = []
Video_Mediaid_List = []

def AppendMediaId(MediaList, MediaId):
    MediaList.append(MediaId)

    if len(MediaList) > 10000:
        MediaList.remove(random.choice(MediaList))
def GetMediaId(MediaList):
    return random.choice(MediaList)

# 获取图灵的回复
def GetTuLingReply(text):
    appkey = "e5ccc9c7c8834ec3b08940e290ff1559"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit'
                             '/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safar'
                             'i/537.36', }
    url = "http://www.tuling123.com/openapi/api?key=%s&info=%s" % (appkey, text)
    content = requests.get(url, headers=headers)

    answer = json.loads(content.text)
    return answer['text']

'''
微信服务器推送消息是xml的，
根据利用ElementTree来解析出的不同xml内容返回不同的回复信息，
就实现了基本的自动回复功能了，也可以按照需求用其他的XML解析方法
'''
import xml.etree.ElementTree as ET

# django默认开启csrf防护，这里使用@csrf_exempt去掉防护
@csrf_exempt
def wechat_auto_reply(request):
    if request.method == "GET":
        # 接收微信服务器get请求发过来的参数
        signature = request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        nonce = request.GET.get('nonce', None)
        echostr = request.GET.get('echostr', None)
        # 服务器配置中的token
        token = 'fly2010love'
        # 把参数放到list中排序后合成一个字符串，再用sha1加密得到新的字符串与微信发来的signature对比，如果相同就返回echostr给服务器，校验通过
        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        hashstr = ''.join([s for s in hashlist])
        hashstr = hashlib.sha1(hashstr).hexdigest()
        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("field")
    else:
        othercontent = autoreply(request)
        #print othercontent
        return HttpResponse(othercontent)



def autoreply(request):
    try:
        webData = request.body
        xmlData = ET.fromstring(webData)

        msg_type = xmlData.find('MsgType').text
        ToUserName = xmlData.find('ToUserName').text
        FromUserName = xmlData.find('FromUserName').text
        CreateTime = xmlData.find('CreateTime').text
        MsgType = xmlData.find('MsgType').text
        MsgId = xmlData.find('MsgId').text

        toUser = FromUserName
        fromUser = ToUserName

        if msg_type == 'text':
            content = xmlData.find('Content').text
            reply = GetTuLingReply(content)
            #print reply
            replyMsg = TextMsg(toUser, fromUser, reply.encode('utf-8'))
            return replyMsg.send()

        elif msg_type == 'image':
            mediaid = xmlData.find('MediaId').text
            AppendMediaId(Image_Mediaid_List, mediaid)

            replyMsg = ImageMsg(toUser, fromUser, GetMediaId(Image_Mediaid_List))
            return replyMsg.send()
        elif msg_type == 'voice':
            mediaid = xmlData.find('MediaId').text
            AppendMediaId(Voice_Mediaid_List, mediaid)

            replyMsg = VoiceMsg(toUser, fromUser, GetMediaId(Voice_Mediaid_List))
            return replyMsg.send()
        elif msg_type == 'video':

            replyMsg = ImageMsg(toUser, fromUser, GetMediaId(Image_Mediaid_List))
            return replyMsg.send()
        elif msg_type == 'shortvideo':
            content = "小视频已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        elif msg_type == 'location':
            content = "位置已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        else:
            msg_type == 'link'
            content = "链接已收到,谢谢"
            replyMsg = TextMsg(toUser, fromUser, content)
            return replyMsg.send()

    except Exception, Argment:
        return Argment

class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


#文本消息回复
class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)

#图片消息回复
class ImageMsg(Msg):
    def __init__(self, toUserName, fromUserName, MediaId):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = MediaId


    def send(self):
        XmlForm = '''
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        '''

        return XmlForm.format(**self.__dict)

#语音消息回复
class VoiceMsg(Msg):
    def __init__(self, toUserName, fromUserName, MediaId):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = MediaId


    def send(self):
        XmlForm = '''
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[voice]]></MsgType>
        <Voice>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Voice>
        </xml>
        '''

        return XmlForm.format(**self.__dict)

#视频消息回复
class VideoMsg(Msg):
    def __init__(self, toUserName, fromUserName, MediaId, title=None, desc = None):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = MediaId
        self.__dict["Title"] = title
        self.__dict["Description"] = desc


    def send(self):
        XmlForm = '''
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[video]]></MsgType>
        <Video>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        '''
        if self.__dict['Title']:
            XmlForm = XmlForm + ''' < Title><![CDATA[{Title}]]></Title>'''

        if self.__dict['Description']:
            XmlForm = XmlForm + '''<Description><![CDATA[{Description}]]></Description>'''

        XmlForm = XmlForm + '''</Video></xml>'''

        return XmlForm.format(**self.__dict)

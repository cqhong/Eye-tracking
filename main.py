from aip import AipSpeech
from ffmpy3 import FFmpeg
import pyaudio
import wave
from urllib.request import urlopen,Request
from urllib.error import URLError
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
import ssl
import websocket
import time

#语音转文字接口参数
""" 你的 APPID AK SK """
APP_ID = '23434237'
API_KEY = 'tapPrEQx9QK47Q56OMSCbqT2'
SECRET_KEY = 'NiS6ZrxYtVP3uYHOufMjgiPr6NFHI0rO'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
#图灵机器人接口参数
class TuringChatMode(object):
    """this mode base on turing robot"""

    def __init__(self):
        # API接口地址
        self.turing_url = 'http://api.tianapi.com/txapi/tuling/index?'

    def get_turing_text(self,text):
        ''' 请求方式:   HTTP POST
            请求参数:   参数      是否必须        长度          说明
                        key        必须          32           APIkey
                        info       必须          1-32         请求内容，编码方式为"utf-8"
                        userid     必须          32           MAC地址或ID
        '''
        turing_url_data = dict(
            key='01884059fcb405fa9f4b17cefb6d712c',
            question=text,

        )
        # print("The things to Request is:",self.turing_url + urlencode(turing_url_data))
        self.request = Request(self.turing_url + urlencode(turing_url_data))
        # print("The result of Request is:",self.request)

        try:
            w_data = urlopen(self.request)
            # print("Type of the data from urlopen:",type(w_data))
            # print("The data from urlopen is:",w_data)
        except URLError:
            raise IndexError("No internet connection available to transfer txt data")
            # 如果发生网络错误，断言提示没有可用的网络连接来传输文本信息
        except:
            raise KeyError("Server wouldn't respond (invalid key or quota has been maxed out)")
            # 其他情况断言提示服务相应次数已经达到上限

        response_text = w_data.read().decode('utf-8')
        # print("Type of the response_text :",type(response_text))
        # print("response_text :",response_text)

        json_result = json.loads(response_text)
        # print("Type of the json_result :",type(json_result))
        return json_result['newslist']


# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:  #rb read to tail
        return fp.read()
#语音转文字接口调用
def speechTOstr():
    path = '1.pcm'  # 文件路径
    if os.path.exists(path):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(path)
        # os.unlink(path)
    else:
        print('no such file:%s')  # 则返回文件不存在
    ff = FFmpeg(executable='C:\\Users\\86158\\Downloads\\ffmpeg-N-100493-gc720286ee3-win64-lgpl-vulkan\\bin\\ffmpeg.exe',inputs={r'D:\pythonProject\SpeechRecognition\1.wav':"-y"},
              outputs={r'D:\pythonProject\SpeechRecognition\1.pcm':"-f s16le -ar 16000 -ac 1 -acodec pcm_s16le"})
    print(ff.cmd)
    ff.run()
    json=client.asr(get_file_content('1.pcm'), 'pcm', 16000, {
        'dev_pid': 1537,
    })
    speechStr=json['result'][0]
    return speechStr

def get_audio():
    # aa = str(input("是否开始录音？   （是/否）"))
    # if aa == str("是") :
        filepath = "1.wav"
        CHUNK = 256
        FORMAT = pyaudio.paInt16
        CHANNELS = 1                # 声道数
        RATE = 16000               # 采样率
        RECORD_SECONDS =3
        WAVE_OUTPUT_FILENAME = filepath
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("*"*10, "开始录音：请在3秒内输入语音")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("*"*10, "录音结束\n")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
#语音合成模块
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        #print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        #print('websocket url :', url)
        return url

def on_message(ws, message):
    try:
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        if status == 2:
            print("语音合成完毕！")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:

            with open('./demo.pcm', 'ab') as f:
                f.write(audio)

    except Exception as e:
        print("receive msg,but parse exception:", e)



# 收到websocket错误的处理
def on_error(ws, error):
    print("")


# 收到websocket关闭的处理
def on_close(ws):
    print("")

# 测试时候在此处正确填写相关信息即可运行
wsParam = Ws_Param(APPID='5fed5e05', APISecret='1c713a090ddaf5aea2b58733e3b7dafc',
                   APIKey='c9cffecb25cd383d030bb36a5140e87e',
                   Text="我在听")

# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        ws.send(d)
        if os.path.exists('./demo.pcm'):
            os.remove('./demo.pcm')

    thread.start_new_thread(run, ())

def get_reply_speech():

    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

#播放音频
def play():
    path = 'reply.wav'  # 文件路径
    if os.path.exists(path):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(path)
        # os.unlink(path)
    else:
        print('no such file:%s')  # 则返回文件不存在
    ff = FFmpeg(
        executable='C:\\Users\\86158\\Downloads\\ffmpeg-N-100493-gc720286ee3-win64-lgpl-vulkan\\bin\\ffmpeg.exe',
        inputs={r'D:\pythonProject\SpeechRecognition\demo.pcm': "-f s16le -ar 16000 -ac 1"},
        outputs={r'D:\pythonProject\SpeechRecognition\reply.wav': ""})
    print(ff.cmd)
    ff.run()
    wf = wave.open("reply.wav", 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data != b'':
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()


turing = TuringChatMode()

while(1):

    get_audio()
    speech=speechTOstr()
    print(speech)
    turing_data=turing.get_turing_text(speech)
    print(turing_data[0]['reply'])
    wsParam.Text="123456"
    reply=turing_data[0]['reply']
    wsParam = Ws_Param(APPID='5fed5e05', APISecret='1c713a090ddaf5aea2b58733e3b7dafc',
                       APIKey='c9cffecb25cd383d030bb36a5140e87e',
                       Text=reply)
    get_reply_speech()
    play()

#ffmpeg -i 1.mp3 -f s16be -ar 16000 -ac 1 -acodec pcm_s16be 1.pcm  ffmpeg cmd命令
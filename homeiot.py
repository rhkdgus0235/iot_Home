from re import L
from signal import pause
from time import sleep
import requests
import json
import sounddevice as sd
import soundfile as sf
from io import BytesIO
from gpiozero import LED,Servo,Button
from pydub import AudioSegment
from pydub.playback import play
import sys
from datetime import datetime
import adafruit_dht
import board
import threading
import paho.mqtt.client as mqtt
from gpiozero import AngularServo
import spidev
from AnalogSpi import AnalogSpi
from FireAlert import FireAlert
from ShadesControl import ShadesControl


# 클래스화는 다음에 할게요 
dhtdevice=adafruit_dht.DHT11(board.D12)
button=Button(21,bounce_time=0.07)
# servo=Servo(19,min_pulse_width=0.0004,max_pulse_width=0.0024)
angle_servo=AngularServo(19, min_angle=-90, max_angle=90, min_pulse_width=0.0004, max_pulse_width=0.0024)
red=LED(16)
now=datetime.now()
ampm = now.strftime('%p')


def recognize():
    global is_success,result

    fs=16000
    seconds=5


    myrecording=sd.rec(int(seconds*fs),samplerate=fs,channels=1)
    sd.wait()

    mem_wav=BytesIO()
    sf.write(mem_wav,myrecording,fs,format="wav")

    print(mem_wav.tell())
    audio=mem_wav.seek(0)

    kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"

    rest_api_key='db7d3e117257f54d58bf7347d49b91b9'

    headers={
        "Content_Type": "applicatioin/octet-stream",
        "X-DSS-Service": "DICTATION",
        "Authorization": "KakaoAK " +rest_api_key,

    }
    # with open('converted.wav','rb') as fp:
    #     audio=fp.read()
    #이것만 교체
    res=requests.post(kakao_speech_url,headers=headers,data=mem_wav)

    print(res.text)

    result_json_string=res.text[
        res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1

    ]
    result=json.loads(result_json_string)
    print(result)
    print(result['value'])

    is_success=True
    start=res.text.find('{"type":"finalResult"')
    end=res.text.rindex('}')+1

    if start==-1:
        start=res.text.find('{"type":"errorCalled"')
        is_success=False

    result_json_string=res.text[start:end]
    result=json.loads(result_json_string)
    return is_success, result

# 음성인식처리

API_KEY='0333a09d025f1976cbb5177a5f6c9b9a'

def get_weather(city='Seoul'):
    URL=f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={API_KEY}&lang=kr'
    print(URL)

    weather={}

    res=requests.get(URL)
    if res.status_code==200:
        result=res.json()
        weather['main']=result['weather'][0]['main']
        weather['description']=result['weather'][0]['description']

        print(result['weather'][0]['description'])
        icon=result['weather'][0]['icon']
        weather['icon'] = f'http://openweathermap.org/img/w/{icon}.png' 
        weather['etc'] = result['main']

    else:
        print('error',res.status_code)

    return weather

weather = get_weather()
print(json.dumps(weather, indent=4, ensure_ascii=False))
weather
# 날씨처리



# print(round(float(weather["etc"]["temp_min"]-273),1))

URL = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
HEADERS={

    "content-Type":"application/xml",
    "Authorization": "KakaoAK db7d3e117257f54d58bf7347d49b91b9"
}
def make_text(text,name="MAN_READ_CALM"):
    return f"""
    <speak>
        <voice name="{name}">{text}</voice>
    </speak>
    """



# 음성합성


def on_connect(client,userdata,flags,rc):
    print("Connected with result code"+str(rc))
    if rc==0:
        client.subscribe("iot/#")
    else:
        print('연결실패:',rc)


def on_message(client,userdata,msg):
    print(msg.topic)
    value=msg.payload.decode()
    if (value=="on" or value=="off"):
        if (value=="on"):
            print('led를 키겠습니다')
            red.on()
        elif(value=="off"):
            print("led를 끄겠습니다")
            red.off()
        # print(f"{float(value)}")  #카메라각도값 제어
        print(f"{msg.topic} {value}")
    
    else:
        angle_servo.angle=float(value)
        print(f"{msg.topic} {value}")

client=mqtt.Client()

client.on_connect=on_connect
client.on_message=on_message


#mqtt제어


key_path='/home/pi/workspace/iot_Home-2/iot_server/access_token.txt'

def send_talk(text,mobile_web_url,web_url=None):
    if not web_url:
        web_url=mobile_web_url
    with open(key_path,'r') as f:
        token=f.read()

    talk_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    header={"Authorization":f"Bearer {token}"}

    text_template={
        'object_type':'text',
        'text':text,
        'link':{
            'web_url':web_url,
            'mobile_web_url':mobile_web_url
            }
    }
    print(text_template)
    payload={'template_object':json.dumps(text_template)}
    res=requests.post(talk_url,data=payload,headers=header)
    return res.json()

def bath_water_detect():
    red.on()
    # res=send_talk('침입 발생','http://192.168.219.105:8000/mjpeg/?mode=stream')
    res=send_talk('목욕 물이 채워졌습니다. 좋은 시간 되세요.','http://www.youtube.com/watch?v=VBFmh3nCZbc')
    # 라파 주소
    if res.get('result_code')!=0:
        print("전송 실패",res['msg'],res['code'])


#카톡연동


# # 딜레이 시간(센서 측정 간격)
# delay = 0.5
# # MCP3008 채널 중 센서에 연결한 채널 설정
# pot_channel0 = 0

# # SPI 인스턴스 spi 생성
# spi = spidev.SpiDev()
# # SPI 통신 시작하기
# spi.open(0, 0)
# # SPI 통신 속도 설정
# spi.max_speed_hz = 100000
# # 0 ~7 까지 8개의 채널에서 SPI 데이터 읽기
# def readadc(adcnum):
#     if adcnum < 0 or adcnum > 7:
#         return -1
#     r = spi.xfer2([1, 8+adcnum <<4, 0])
#     data = ((r[1] & 3) << 8) + r[2]
#     return data

#물높이 센서(spi)

# def sensor_data():
    
#     while True:
#         if i==5:
#             return
#         pot_value0 = readadc(pot_channel0)
#         print(pot_value0)
#         if pot_value0>700:
# #센서값을 통한 카톡메세지 전달
#             bath_water_detect()
#             i+=1
            
#         sleep(5)


def analog_sensors():
    i=0
    analog_spi=AnalogSpi()
    shades_control=ShadesControl()
    fire_alert=FireAlert()

    while True:
        
        pot_value0 = analog_spi.readadc(analog_spi.pot_channel0)
        pot_value1 = analog_spi.readadc(analog_spi.pot_channel1)
        pot_value2 = analog_spi.readadc(analog_spi.pot_channel2)
        
        fire_alert.run(pot_value0)
        shades_control.run(pot_value1)

        if i==5:
            return
        print(pot_value2)
        if pot_value2>700:
#센서값을 통한 카톡메세지 전달
            bath_water_detect()
            i+=1
            
        sleep(2)



# button.when_pressed=recognize
while True:
    try:
        
        # pot_value0_th=threading.Thread(target=readadc,args=(pot_channel0,))
        # pot_value0_th.start()
        t=threading.Thread(target=analog_sensors,args=())
        
        t.start()
        # pot_value0_th.start()
        
        # print(pot_value0)
        # if pot_value0>650:
        #     t=threading.Thread(target=bath_water_detect)
        #     t.start()
        #     sleep(2)
        client.connect("192.168.219.104")  #pc주소입력해야함
        client.loop_start()
    

    except Exception as e:
        print(f'에러:{e}')


    button.wait_for_press()
    recognize()
    if is_success:
        print('인식결과',result['value'])
        print(type(result['value']))

        if(result['value']=="창문 열어" or result['value']=="창문 열어줘" or result['value']=="창문 좀 열어" or result['value']=="창문 좀 열어줘"):
            angle_servo.angle=60
            sleep(1)
            
            print("창문열게요")
            # result['value']="초기화"
            # print(result['value'])
            
        elif(result['value']=="창문 닫아" or result['value']=="창문 닫아줘" or result['value']=="창문 좀 닫아" or result['value']=="창문 좀 닫아줘"):
            # servo.max()
            angle_servo.angle=-60
            sleep(1)
            
            print("문 닫을게요")
        elif(result['value']=="거실 불 켜" or result['value']=="거실 켜" or result['value']=="거실 불" or result['value']=="거실 불 좀 켜"):
            print("전등 킬게요")
            red.on()
            sleep(1)
        elif(result['value']=="거실 불 꺼" or result['value']=="거실 꺼" or result['value']=="거실 불 좀 꺼"):
            print("전등 끌게요")
            red.off()
            sleep(1)

        elif(result['value']=="날씨 알려줘"):
            text=f'''오늘 날씨는 {weather["description"]} 최저온도는 {round(float(weather["etc"]["temp_min"]-273),1)} 도
            최고온도는 {round(float(weather["etc"]["temp_max"]-273),1)} 도입니다 
            또한 습도는 {weather['etc']['humidity']} 입니다. 좋은 하루 되세요
            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)

        elif(result['value']=="시간 알려줘"):
            ampm_kr = '오전' if ampm == 'AM' else '오후'
            print(ampm_kr)
            if now.hour>12:
                time_now=now.hour-12
            text=f'''현재 시간은 {ampm_kr}  {time_now}시 {now.minute}분입니다.
            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)

        elif(result['value']=="실내 온도 알려줘"):
            temparature_c=dhtdevice.temperature
            text=f'''{temparature_c} 도 입니다

            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)
        
        elif(result['value']=="실내 습도 알려줘"):
            humidity=dhtdevice.humidity
            text=f'''{humidity} 퍼센트 입니다

            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)
            

        elif(result['value']=="종료해"):
            break

        elif(result['value']!="문 열어" or result['value']!="문 닫아" or result['value']!="전등 켜" or result['value']!="전등 꺼" or result['value']!="날씨 알려줘" or result['value']!="종료해"):
            # result['value']="초기화"
            
            text=f'''죄송합니다 다시 말씀해주세요
            '''
            print(text)
            
            data=make_text(text)
            res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

            sound=BytesIO(res_sound.content)
            song=AudioSegment.from_mp3(sound)
            play(song)



        # elif(result['value']=="초기화"):
        #     continue

        
    else:
        print("인식실패:",result['value'])

# 클래스화는 다음에 할게요
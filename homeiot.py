from re import L
from signal import pause
from time import sleep
import requests
import json
import sounddevice as sd
import soundfile as sf
from io import BytesIO
from gpiozero import LED,Servo,Button,PWMLED
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
red=PWMLED(16)
green=PWMLED(13)
blue=PWMLED(26)
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

living_true=0
kitchen_true=0
mainroom_true=0
listI=[]
for i in range(0,101):
    listI.append(i)

listS=list(map(str,listI))

def on_connect(client,userdata,flags,rc):
    print("Connected with result code"+str(rc))
    if rc==0:
        client.subscribe("iot/#")
    else:
        print('연결실패:',rc)


def on_message(client,userdata,msg):
    global living_true,kitchen_true,mainroom_true
    print(msg.topic)
    mt=msg.topic
    
    value=msg.payload.decode()
    if (mt=="iot/led/livingroom" or mt=="iot/led/kitchen" or mt=="iot/led/mainroom"):
        if (mt=="iot/led/livingroom" and value=="on"):
            print('거실led를 키겠습니다')
            
            living_true=1
            red.value=0.5
            
        elif(mt=="iot/led/livingroom" and value=="off"):
            print("거실led를 끄겠습니다")
            living_true=0
            red.off()
        elif(mt=="iot/led/kitchen" and value=="on"):
            print("주방led를 키겠습니다")
            kitchen_true=1
            green.value=0.5
        elif(mt=="iot/led/kitchen" and value=="off"):
            print("주방led를 끄겠습니다")
            kitchen_true=0
            green.off()
        elif(mt=="iot/led/mainroom" and value=="on"):
            print("안방led를 끄겠습니다")
            mainroom_true=1
            blue.value=0.5
        elif(mt=="iot/led/mainroom" and value=="off"):
            print("안방led를 끄겠습니다")
            mainroom_true=0
            blue.off()
        elif(living_true==1 and mt=="iot/led/livingroom"):
            
            if (value in listS):
                print(living_true)
                print(float(int(value)/100))
                red.value=float(int(value)/100)
        elif(kitchen_true==1 and mt=="iot/led/kitchen"):
            
            if (value in listS):
                print(kitchen_true)
                print(float(int(value)/100))
                green.value=float(int(value)/100)
        
        elif(mainroom_true==1 and mt=="iot/led/mainroom"):
            
            if (value in listS):
                print(mainroom_true)
                print(float(int(value)/100))
                blue.value=float(int(value)/100)



        # print(f"{float(value)}")  #카메라각도값 제어
        print(f"{msg.topic} {value}")
    
    else:
        if(msg.topic=="iot/blind"):
            print("블라각 제어")
            angle_servo.angle=float(value)
            print(f"{msg.topic} {value}")
        elif(msg.topic=="iot/camera/angle"):
            print("카메라각 제어")
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




# 아날로그 센서 
def analog_sensors():
    
    analog_spi=AnalogSpi()
    shades_control=ShadesControl() #서보모터의 gpio 핀은 기본 22로 설정되어있음
    fire_alert=FireAlert()

    while True:
        
        pot_value0 = analog_spi.readadc(analog_spi.pot_channel0)
        pot_value1 = analog_spi.readadc(analog_spi.pot_channel1)
        pot_value2 = analog_spi.readadc(analog_spi.pot_channel2)

        # 불꽃감지
        fire_alert.run(pot_value0)

        # 조도센서 블라인드 
        shades_control.run(pot_value1)

        # 물높이
        print(pot_value2)
        if pot_value2>680:
            bath_water_detect()
            sleep(295)
            
        sleep(2)



while True:
    try:

        t=threading.Thread(target=analog_sensors,args=())
        t.start()
        
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

        elif(result['value']=="주방 불 켜" or result['value']=="주방 켜" or result['value']=="주방 불" or result['value']=="주방 불 좀 켜"):
            print("전등 킬게요")
            green.on()
            sleep(1)
        elif(result['value']=="주방 불 꺼" or result['value']=="주방 꺼" or result['value']=="주방 불 좀 꺼"):
            print("전등 끌게요")
            green.off()
            sleep(1)

        elif(result['value']=="안방 불 켜" or result['value']=="안방 켜" or result['value']=="안방 불" or result['value']=="안방 불 좀 켜"):
            print("전등 킬게요")
            blue.on()
            sleep(1)
        elif(result['value']=="안방 불 꺼" or result['value']=="안방 꺼" or result['value']=="안방 불 좀 꺼"):
            print("전등 끌게요")
            blue.off()
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
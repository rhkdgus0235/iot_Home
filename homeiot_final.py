from send_kakaotalk import key_path
from bath_water import bath_water_detect
from voice_systhesize import URL,HEADERS,make_text
from voice_recognize import *
from get_weather_seoul import get_weather
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
import os
import cv2
from AnalogSpi import AnalogSpi
from FireAlert import FireAlert
from Record import Record




dhtdevice=adafruit_dht.DHT11(board.D12)
button=Button(21,bounce_time=0.07)
# servo=Servo(19,min_pulse_width=0.0004,max_pulse_width=0.0024)
angle_blind=AngularServo(19, min_angle=-90, max_angle=90, min_pulse_width=0.0004, max_pulse_width=0.0024)
angle_camera=AngularServo(23, min_angle=-90, max_angle=90, min_pulse_width=0.0004, max_pulse_width=0.0024)
red=PWMLED(16)
green=PWMLED(13)
blue=PWMLED(26)
now=datetime.now()
ampm = now.strftime('%p')
record=Record()




living_true=0
kitchen_true=0
mainroom_true=0
automode_true=0

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
    global living_true,kitchen_true,mainroom_true, thread_state,automode_true,shade_state
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


        print(f"{msg.topic} {value}")
    
    else:
        if(msg.topic=="iot/blind" and value=="automode_on" ):
            automode_true=1
            shade_state=True
            print(shade_state)
            count=0
            if (automode_true==1 and shade_state==True):
                if count==0:
                    shades_thread=threading.Thread(target=analog_sensor_shade,args=())
                    shades_thread.start()
                    count+=1

        elif(msg.topic=="iot/blind" and value=="automode_off"):
            automode_true=0
            shade_state=False
            
            print(shade_state)
        elif(msg.topic=="iot/camera/angle"):
            print("카메라각 제어")
            angle_camera.angle=float(value)
            print(f"{msg.topic} {value}")
        elif(msg.topic=="iot/camera/capture" and value=="captured"):
            print("내부카메라 캡쳐 ")
            cap=cv2.VideoCapture(1)
    
            retval, frame=cap.read()  
            start=datetime.now()
            fname=start.strftime('./data/%Y%m%d_%H%M%S.png')
            cv2.imwrite(fname,frame, params=[cv2.IMWRITE_PNG_COMPRESSION,0])
        elif(msg.topic=="iot/camera/record" and value=="on"):
            
            print("내부카메라 녹화")
            t_record=threading.Thread(target=record.record_thread,args=())
            t_record.start()
            
            
        elif (msg.topic=="iot/camera/record" and value=="off"):
            print("내부카메라 녹화종료")
            
            record.thread_state = False
        elif (automode_true==0 and mt=="iot/blind"):
            if (value in listS):
                print("블라각 제어")
                angle_blind.angle=float(value)
                print(f"{msg.topic} {value}")
       



#mqtt제어



def send_talk_alert(text,mobile_web_url,web_url=None):
    if not web_url:
        web_url=mobile_web_url
    with open(key_path,'r') as f:
        token=f.read()

    talk_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    header={"Authorization":f"Bearer {token}"}

    text_template={
        'object_type':'text',
        'text':text,
        # 'image_url': "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
        'link':{
            'web_url':web_url,
            'mobile_web_url':mobile_web_url
            }
    }
    print(text_template)
    payload={'template_object':json.dumps(text_template)}
    res=requests.post(talk_url,data=payload,headers=header)
    return res.json()




class ShadesControl:
  def __init__(self):
    
    self.dc = 7.5
    angle_blind.value=self.dc/100
    

  def is_night(self):
    hour=datetime.now().hour
    if hour < 6 or hour>19 :
      return True
    else:
      return False

  def run(self,sensor_value):
    # while문 안에 넣을것
    try:
      if(self.is_night()):
        #밤일때
        if sensor_value<1000:
          print("is_night= true, 조도센서 1000보다 큼")
          try:
            if self.dc < 12.5*100 :
              
              self.dc += 0.1 *100
              angle_blind.value=self.dc/100
            else:
                self.dc+=0
                angle_blind.value=self.dc/100
          except KeyboardInterrupt:
            self.dc+=0
            angle_blind.value=self.dc/100
        else:
            self.dc+=0
            angle_blind.value=self.dc/100
      else:
        #낮일때
        if sensor_value>450:
          print("is_night= false, 조도센서 450보다 작음")
          try:
            if self.dc > 2.5 *100 :
              
              self.dc -= 0.1 *100
              angle_blind.value=self.dc/100
            else:
                self.dc+=0
                angle_blind.value=self.dc/100

          except KeyboardInterrupt:
            self.dc+=0
            angle_blind.value=self.dc/100    
        else:
            self.dc+=0
            angle_blind.value=self.dc/100

    except KeyboardInterrupt:
        self.dc+=0
        angle_blind.value=self.dc/100



# 아날로그 센서 

def analog_sensors():
    i=0
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
        # shades_control.run(pot_value1)

        # 물높이
        
        print("불꽃감지 값:",pot_value0)
        
        print("물높이:", pot_value2)
        if pot_value2>600 and i==0:
            bath_water_detect()
            sleep(5)
            i+=1
        sleep(2)

    




shade_state=True
def analog_sensor_shade():
    analog_spi=AnalogSpi()
    shades_control=ShadesControl() #서보모터의 gpio 핀은 기본 22로 설정되어있음
    while shade_state:
        pot_value1 = analog_spi.readadc(analog_spi.pot_channel1)
        print("조도 값:",pot_value1)
        
        shades_control.run(pot_value1)
        sleep(2)

#센서값을 통한 카톡메세지 전달

def main():
    weather = get_weather()
    print(json.dumps(weather, indent=4, ensure_ascii=False))
    weather

    client=mqtt.Client()

    client.on_connect=on_connect
    client.on_message=on_message

    t=threading.Thread(target=analog_sensors,args=())
            
    t.start()
    client.connect("192.168.219.103")  #pc주소입력해야함
    client.loop_start()
    text=f'''안녕하세요 스마트홈 작동을 시작하겠습니다.
    '''
    print(text)

    data=make_text(text)
    res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

    sound=BytesIO(res_sound.content)
    song=AudioSegment.from_mp3(sound)
    play(song)

    while True:
        try:
            
            print("시작하겠습니다")
        
        except Exception as e:
            print(f'에러:{e}')


        button.wait_for_press()
        
        is_success,result=recognize()
        
        if is_success:
            print('인식결과',result['value'])
            print(type(result['value']))

            if(result['value']=="창문 열어" or result['value']=="창문 열어줘" or result['value']=="창문 좀 열어" or result['value']=="창문 좀 열어줘"):
                angle_blind.angle=60
                sleep(1)
                
                print("창문열게요")
                
                
            elif(result['value']=="창문 닫아" or result['value']=="창문 닫아줘" or result['value']=="창문 좀 닫아" or result['value']=="창문 좀 닫아줘"):
                
                angle_blind.angle=-60
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

            else: 
                text=f'''죄송합니다 다시 말씀해주세요
                '''
                print(text)
                
                data=make_text(text)
                res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

                sound=BytesIO(res_sound.content)
                song=AudioSegment.from_mp3(sound)
                play(song)

            
        else:
            print("인식실패:",result['value'])


main()
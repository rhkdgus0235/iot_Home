import paho.mqtt.client as mqtt
from gpiozero import AngularServo
import sqlite3
# con=sqlite3.connect('iot.db')
# cursor=con.cursor()
servo = AngularServo(19, min_angle=-90, max_angle=90, min_pulse_width=0.0004, max_pulse_width=0.0024)
def on_connect(client,userdata,flags,rc):
    print("Connected with result code"+str(rc))
    if rc==0:
        client.subscribe("iot/#")
    else:
        print('연결실패:',rc)


def on_message(client,userdata,msg):
    print(msg.topic)
    value=msg.payload.decode()
    if (value=="on"):
        print('led를 키겠습니다')
    elif(value=="off"):
        print("led를 끄겠습니다")
    print(f"{float(value)}")  #카메라각도값 제어
    print(f"{msg.topic} {value}")
    servo.angle=float(value)
    # (_,user,place,sensor)=msg.topic.split('/')
    # sql=f'''INSERT INTO sensors(user,place,sensor,value)
    #         values('{user}','{place}','{sensor}',{value})'''

    # cursor.execute(sql)
    # con.commit()


client=mqtt.Client()

client.on_connect=on_connect
client.on_message=on_message


try:
    client.connect("192.168.219.104")  #pc주소입력해야함
    client.loop_forever()
    

except Exception as e:
    print(f'에러:{e}')
    # cursor.close()
    # con.close()


from time import sleep

sleep(20)
print("프로그램을 종료합니다")





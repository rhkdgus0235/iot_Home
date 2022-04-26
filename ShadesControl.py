from AnalogSpi import AnalogSpi
import RPi.GPIO as GPIO
import time
from datetime import datetime
from FireAlert import FireAlert
from gpiozero import AngularServo

# 오전 창문열고 오후면 창문닫는다
# 아침 6시~ 저녁 8시 열고 나중 닫음 

# ============
# 천으로가림 1000
# 어두운 방 800
# 밝은방 440~550
# 손전등 200~100

# ===========
# 낮에는 조도센서 값이 450 이상이 될때까지 
# 시간 딜레이를 줘가면서 도어모터를 여는쪽으로 작동 
# 값이 450가 안되더라도 도어모터 끝이면 그만작동

# 밤에는 if값이 조도센서값 1000 이하인 거, 도어모터가 닫히는 방향인 거 외에 동일한 작동 

# 지터링이 심하다 시간나면 앵귤러서보모터 클래스로 바꿔볼것 

class ShadesControl:
  def __init__(self,SERVO_PIN = 22):
    self.SERVO_PIN = SERVO_PIN 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    self.servo = GPIO.PWM(SERVO_PIN,50)
    self.servo.start(0)
    self.dc = 7.5
    self.servo.ChangeDutyCycle(self.dc)


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
          print("밤, 조도센서 1000보다 큼")
          try:
            if self.dc < 12.5 :
              self.servo.start(0)
              self.dc += 0.1
              self.servo.ChangeDutyCycle(self.dc)
            else:
              self.servo.stop()
              print("모터 끝이라 작동x")
          except KeyboardInterrupt:
            self.servo.stop()
            GPIO.cleanup()
        else:
                self.servo.stop()
      else:
        #낮일때
        if sensor_value>450:
          print("낮, 조도센서 450보다 작음")
          try:
            if self.dc > 2.5 :
              self.servo.start(0)
              self.dc -= 0.1
              self.servo.ChangeDutyCycle(self.dc)
            else:
              self.servo.stop()
              print("모터 끝이라 작동x")

          except KeyboardInterrupt:
            self.servo.stop()
            GPIO.cleanup()      
        else:
            self.servo.stop()

    except KeyboardInterrupt:
      self.servo.stop()
      GPIO.cleanup()      


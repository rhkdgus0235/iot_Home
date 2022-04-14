from AnalogSpi import AnalogSpi
from ShadesControl import ShadesControl
from FireAlert import FireAlert
import time

a = AnalogSpi()
s = ShadesControl()
f =FireAlert()


while True:
  # readadc 함수로 pot_channel의 SPI 데이터를 읽기
  pot_value0 = a.readadc(a.pot_channel0)
  pot_value1 = a.readadc(a.pot_channel1)
  print("---------------------------")
  print(f"불꽃감지 value: {pot_value0}" ) 
  print(f"조도센서 LDR value: {pot_value1}") 

  f.run(pot_value0)
  s.run(pot_value1)
  time.sleep(a.delay)
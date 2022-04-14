import spidev

class AnalogSpi :
  def __init__(self,input_chanel=0,delay = 0.5):

      # 딜레이 시간(센서 측정 간격)
    self.delay = delay
    
    # MCP3008 채널 중 센서에 연결한 채널 설정
    self.pot_channel0 = 0
    self.pot_channel1 = 1
    self.pot_channel2 = 2
    self.pot_channel3 = 3
    self.pot_channel4 = 4
    self.pot_channel5 = 5
    self.pot_channel6 = 6
    self.pot_channel7 = 7

    self.input_chanel=input_chanel

    # SPI 인스턴스 spi 생성
    self.spi = spidev.SpiDev()

    # SPI 통신 시작하기
    self.spi.open(input_chanel, 0)
    # SPI 통신 속도 설정
    self.spi.max_speed_hz = 100000
    # 0 ~7 까지 8개의 채널에서 SPI 데이터 읽기
  def readadc(self, adcnum):
    if adcnum < 0 or adcnum > 7:
      return -1
    r = self.spi.xfer2([1, 8+adcnum <<4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

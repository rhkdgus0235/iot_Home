from send_kakaotalk import send_talk
def bath_water_detect():
    # red.on()
    # res=send_talk('침입 발생','http://192.168.219.105:8000/mjpeg/?mode=stream')
    res=send_talk('목욕 물이 채워졌습니다. 좋은 시간 되세요.','http://www.youtube.com/watch?v=VBFmh3nCZbc')#카카오톡 개발자 사이트에서 youtube.com 등록
    # 라파 주소
    if res.get('result_code')!=0:
        print("전송 실패",res['msg'],res['code'])

import json
import requests

key_path='/home/pi/workspace/iot_Home-2/iot_server/access_token.txt'

def send_talk(text,mobile_web_url,web_url=None):
    if not web_url:
        web_url=mobile_web_url
    with open(key_path,'r') as f:
        token=f.read()

    talk_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    header={"Authorization":f"Bearer {token}"}

    # text_template={
    #     'object_type':'text',
    #     'text':text,
    #     'image_url': "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
    #     'link':{
    #         'web_url':web_url,
    #         'mobile_web_url':mobile_web_url
    #         }
    # }
    text_template={
        'object_type':'feed',
        "content": {
            "title": "즐거운 시간",
            "description": text, 
            "image_url": "https://c.pxhere.com/photos/02/7b/hammocks_trees_summer_relaxation_resort_relax_holiday_tranquil-947005.jpg!d", "image_width": 640,
            "image_height": 640, 
            "link": {
            "web_url": web_url,
            "mobile_web_url": mobile_web_url,
            "android_execution_params": "contentId=100", "ios_execution_params": "contentId=100"
        } 
        }
        
    }


    print(text_template)
    payload={'template_object':json.dumps(text_template)}
    res=requests.post(talk_url,data=payload,headers=header)
    return res.json()
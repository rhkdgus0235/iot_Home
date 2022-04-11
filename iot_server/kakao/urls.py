from django.urls import path
from kakao.views import *

app_name="kakao"
urlpatterns=[
    path('login/',KaKaoLoginView.as_view(),name="login"),
    path('oauth/',KakaoAuthView.as_view(),name="oauth"),
    path('talk/', KakaoTalkView.as_view(), name="talk"),
]
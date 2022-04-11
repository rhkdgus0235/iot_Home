from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse,StreamingHttpResponse
from mjpeg.picam import MJpegStreamCam
from time import sleep
mjpegStream=MJpegStreamCam()
# Create your views here.
class CamView(TemplateView):
    template_name="cam.html"

    def get_context_data(self):
        context=super().get_context_data()
        context["mode"]=self.request.GET.get("mode","#")
        return context

def snapshot(request):
    sleep(2)
    image=mjpegStream.snapshot()
    return HttpResponse(image,content_type="image/jpeg")

def stream(request):

    return StreamingHttpResponse(mjpegStream,content_type='multipart/x-mixed-replace;boundary=--myboundary')

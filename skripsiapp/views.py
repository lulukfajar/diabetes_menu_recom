from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template import loader

def landingpage(request):
  template = loader.get_template('landingpage.html')
  return HttpResponse(template.render())
def inputpage(request):
  template = loader.get_template('inputpage.html')
  return HttpResponse(template.render())
def menupage(request):
  template = loader.get_template('menupage.html')
  return HttpResponse(template.render())
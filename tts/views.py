from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from .models import Tools, TTSModels
# Create your views here.

class SelectionView(FormView):
   def get(self, request):
      return render(request, 'tts/index.html')

   def post(self, request, *args, **kwargs):
      return redirect('/connect')
     

class ConnectView(TemplateView):
   def get(self, request):
      print(request)
      return render(request, 'tts/index.html')

   def post(self, request, *args, **kwargs):
      return redirect('/')

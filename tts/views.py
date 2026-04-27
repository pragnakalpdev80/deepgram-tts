from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from .models import Tools, TTSModels
# Create your views here.

class SelectionView(FormView):
   def get(self, request):
      models = TTSModels.objects.filter(is_deleted=False).select_related('tool')
      return render(request, 'tts/index.html', {'models': models})
   
   def post(self, request, *args, **kwargs):
      model_id = request.POST.get('model')
      try:
         tts_model = TTSModels.objects.select_related('tool').get(id=model_id)
         request.session['model_id'] = tts_model.model_id
         request.session['tool'] = tts_model.tool.name.lower()  
         request.session['model_name'] = tts_model.name
      except TTSModels.DoesNotExist:
         return redirect('/')
      return redirect('/connect/')
     

class ConnectView(TemplateView):
   def get(self, request):
      model_id = request.session.get('model_id', '')
      tool = request.session.get('tool', '')
      model_name = request.session.get('model_name', '')
      return render(request, 'tts/connect.html', {
         'model_id': model_id,
         'tool': tool,
         'model_name': model_name,
      })

   def post(self, request, *args, **kwargs):
      text = request.POST.get()
      print(text)
      return redirect('/')
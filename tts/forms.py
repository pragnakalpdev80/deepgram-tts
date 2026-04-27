# from django import forms
# from .models import TTSModels

# class TTSConfig(forms.ModelForm):
#     # tool = forms.ModelChoiceField(
#     #     queryset=Tools.objects.filter(is_deleted=False),
#     #     label="Tool"
#     # )

#     # model = forms.ModelChoiceField(
#     #     queryset=TTSModels.objects.filter(is_deleted=False).select_related('tool'),
#     #     label="Model"
#     # )

#     def clean(self):
#         cleaned_data = super().clean()
#         # tool = cleaned_data.get("tool")
#         model = cleaned_data.get("model")
#         # if tool and model and model.tool != tool:
#         #    raise forms.ValidationError("model", "Selected model does not belong to the chosen provider.")
#         return cleaned_data
    
#     class Meta:
#         model = TTSModels
#         fields = ['model']
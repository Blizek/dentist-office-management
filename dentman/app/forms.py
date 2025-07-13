from django import forms

from dentman.app.models import Attachment

class AttachmentAdminForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = '__all__'
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.pdf, .jpg, .png, .mp4'}),
        }

from django import forms

from dentman.man.models import Employment

class EmploymentAdminForm(forms.ModelForm):
    class Meta:
        model = Employment
        fields = '__all__'
        widgets = {
            'contract_scan': forms.FileInput(attrs={'accept': '.pdf'}),
        }
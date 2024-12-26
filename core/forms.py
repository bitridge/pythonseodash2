from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, Client, Project, SEOLog, ReportSection, Media

class CustomUserForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'role')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password')

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'website', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client', 'description', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': False}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        return cleaned_data

class SEOLogForm(forms.ModelForm):
    class Meta:
        model = SEOLog
        fields = ['project', 'date', 'on_page_work', 'off_page_work']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'on_page_work': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'off_page_work': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role == 'provider':
            # Filter projects based on SEO logs created by the provider
            self.fields['project'].queryset = Project.objects.filter(seolog__created_by=user).distinct()

class ReportSectionForm(forms.ModelForm):
    class Meta:
        model = ReportSection
        fields = ['project', 'title', 'content', 'image', 'order']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['seo_log', 'file', 'file_type', 'description']
        widgets = {
            'seo_log': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_file_type(self):
        file = self.cleaned_data.get('file')
        file_type = self.cleaned_data.get('file_type')
        
        if file:
            # Auto-detect file type based on extension
            extension = file.name.split('.')[-1].lower()
            if extension in ['jpg', 'jpeg', 'png', 'gif']:
                return 'image'
            elif extension in ['pdf', 'doc', 'docx']:
                return 'document'
            elif extension in ['xls', 'xlsx', 'csv']:
                return 'spreadsheet'
        return file_type 
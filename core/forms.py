from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, Client, Project, SEOLog, ReportSection, Media, SEOLogFile

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
        fields = ['name', 'client', 'description', 'providers']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'providers': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        return cleaned_data

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class SEOLogForm(forms.ModelForm):
    on_page_files = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        help_text='Upload files related to on-page SEO work'
    )
    off_page_files = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        help_text='Upload files related to off-page SEO work'
    )
    providers = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='provider'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    class Meta:
        model = SEOLog
        fields = [
            'project', 'date', 'on_page_work', 'on_page_description',
            'off_page_work', 'off_page_description', 'providers'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'on_page_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'off_page_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'on_page_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the on-page SEO work performed...'
            }),
            'off_page_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the off-page SEO work performed...'
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.role == 'provider':
            self.fields['project'].queryset = Project.objects.filter(
                seolog__created_by=user
            ).distinct()
        elif user.role == 'admin':
            self.fields['project'].queryset = Project.objects.all()
        else:
            self.fields['project'].queryset = Project.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Handle file uploads for on-page work
            for file in self.files.getlist('on_page_files'):
                SEOLogFile.objects.create(
                    seo_log=instance,
                    file=file,
                    work_type='on_page',
                    file_name=file.name,
                    file_type=file.content_type,
                    file_size=file.size
                )
            # Handle file uploads for off-page work
            for file in self.files.getlist('off_page_files'):
                SEOLogFile.objects.create(
                    seo_log=instance,
                    file=file,
                    work_type='off_page',
                    file_name=file.name,
                    file_type=file.content_type,
                    file_size=file.size
                )
            # Handle provider assignments
            if 'providers' in self.cleaned_data:
                instance.providers.set(self.cleaned_data['providers'])
        return instance

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
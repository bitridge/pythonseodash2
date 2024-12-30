from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser, Customer, Project, SEOLog, ReportSection, Media, SEOLogFile, Report, ReportAttachment, ReportSectionOrder
from django.utils import timezone

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields.pop('role', None)  # Remove role field for non-admin users

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
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
        fields = ['name', 'customer', 'description', 'providers', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'providers': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields.pop('providers', None)  # Remove providers field for non-admin users

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
    files = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        help_text='Upload files related to SEO work'
    )

    class Meta:
        model = SEOLog
        fields = ['project', 'work_type', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the SEO work performed...'
            })
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter projects based on user role
        if user.role == 'provider':
            self.fields['project'].queryset = Project.objects.filter(providers=user)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:  # Only for new instances
            instance.date = timezone.now().date()
        if commit:
            instance.save()
            # Handle file uploads
            if self.cleaned_data.get('files'):
                for file in self.cleaned_data['files']:
                    SEOLogFile.objects.create(
                        seo_log=instance,
                        file=file,
                        work_type=instance.work_type
                    )
        return instance

class ReportSectionForm(forms.ModelForm):
    class Meta:
        model = ReportSection
        fields = ['title', 'content', 'priority', 'files', 'seo_logs']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6, 'class': 'summernote'}),
            'priority': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'files': forms.SelectMultiple(attrs={'class': 'select2'}),
            'seo_logs': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        if priority < 1:
            raise forms.ValidationError("Priority must be 1 or greater")
        return priority

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

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'status', 'is_template']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_template': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.role != 'admin':
            # Providers can only create draft reports
            self.fields['status'].choices = [('draft', 'Draft')]
            self.fields['is_template'].widget = forms.HiddenInput()
        
        if self.instance.pk:
            # Can't change status back to draft once it's been reviewed/published
            if self.instance.status in ['approved', 'published', 'archived']:
                self.fields['status'].widget.attrs['disabled'] = True

    def clean(self):
        cleaned_data = super().clean()
        if not self.data.get('section_title'):
            raise forms.ValidationError("Section title is required")
        if not self.data.get('content'):
            raise forms.ValidationError("Section content is required")
        
        # Status validation
        status = cleaned_data.get('status')
        if self.instance.pk and self.instance.status in ['approved', 'published', 'archived']:
            if status != self.instance.status:
                raise forms.ValidationError("Cannot change status of approved/published reports")
        
        return cleaned_data

class ReportAttachmentForm(forms.ModelForm):
    class Meta:
        model = ReportAttachment
        fields = ['title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 50MB)
            if file.size > 52428800:
                raise forms.ValidationError("File size must be under 50MB")
            
            # Check file type
            allowed_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg', 'gif']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_types:
                raise forms.ValidationError(f"File type not supported. Allowed types: {', '.join(allowed_types)}")
        return file

class ReportSectionOrderForm(forms.ModelForm):
    class Meta:
        model = ReportSectionOrder
        fields = ['order', 'page_break_before']
        widgets = {
            'order': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_order(self):
        order = self.cleaned_data.get('order')
        if order < 1:
            raise forms.ValidationError("Order must be 1 or greater")
        return order 
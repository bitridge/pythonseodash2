from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    CustomUser, Customer, Project, SEOLog, ReportSection, 
    Media, SEOLogFile, Report, ReportAttachment, ReportSectionOrder
)

# Custom File Upload Widgets and Fields
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

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
        fields = ['name', 'customer', 'description', 'providers', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'providers': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.Select(attrs={'class': 'form-select'}, choices=[(True, 'Active'), (False, 'Inactive')])
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role != 'admin':
            self.fields.pop('providers', None)  # Remove providers field for non-admin users
        
        # Set default value for is_active to True for new projects
        if not self.instance.pk:  # If this is a new project
            self.initial['is_active'] = True

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        return cleaned_data

class SEOLogForm(forms.ModelForm):
    files = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control file-input',
            'accept': '.jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.xls,.xlsx',
            'data-browse-label': 'Browse Files',
            'style': 'cursor: pointer;'
        })
    )

    class Meta:
        model = SEOLog
        fields = ['project', 'date', 'work_type', 'description']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control summernote',
                'rows': 4,
                'placeholder': 'Enter work description'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter projects based on user role
            if user.role == 'provider':
                self.fields['project'].queryset = Project.objects.filter(providers=user)
            elif user.role == 'customer':
                self.fields['project'].queryset = Project.objects.filter(customer=user)
            else:
                # Admin can see all projects
                self.fields['project'].queryset = Project.objects.all()

            # Set default date to today if not set
            if not self.instance.pk:
                self.initial['date'] = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        files = self.files.getlist('files')
        
        # Validate file sizes and types
        max_size = 50 * 1024 * 1024  # 50MB
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        
        for file in files:
            if file.size > max_size:
                self.add_error('files', f'File {file.name} is too large. Maximum size is 50MB.')
            if file.content_type not in allowed_types:
                self.add_error('files', f'File {file.name} has an unsupported format.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
            
            # Handle file uploads
            files = self.files.getlist('files')
            if files:
                for file in files:
                    # Get file extension
                    ext = file.name.split('.')[-1].lower()
                    # Determine file type based on extension
                    if ext in ['jpg', 'jpeg', 'png', 'gif']:
                        file_type = 'image'
                    elif ext in ['pdf', 'doc', 'docx']:
                        file_type = 'document'
                    elif ext in ['xls', 'xlsx']:
                        file_type = 'spreadsheet'
                    else:
                        file_type = 'other'
                    
                    SEOLogFile.objects.create(
                        seo_log=instance,
                        file=file,
                        work_type=instance.work_type,
                        file_name=file.name,
                        file_type=file_type,
                        file_size=file.size
                    )
        return instance

class ReportForm(forms.ModelForm):
    title = forms.CharField(
        label='Report Title',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter report title'
        })
    )
    
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter report description'
        })
    )
    
    selected_logs = forms.ModelMultipleChoiceField(
        label='Select Work Logs',
        queryset=SEOLog.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'log-checkbox'
        })
    )
    
    class Meta:
        model = Report
        fields = ['title', 'description']

    def __init__(self, *args, project=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            # Filter logs based on user role and project
            if user and hasattr(user, 'role'):
                if user.role == 'provider':
                    self.fields['selected_logs'].queryset = SEOLog.objects.filter(
                        project=project,
                        created_by=user
                    )
                elif user.role == 'customer':
                    self.fields['selected_logs'].queryset = SEOLog.objects.filter(
                        project=project,
                        project__customer=user
                    )
                else:  # admin or superuser
                    self.fields['selected_logs'].queryset = SEOLog.objects.filter(
                        project=project
                    )
            else:
                self.fields['selected_logs'].queryset = SEOLog.objects.filter(project=project)

    def clean(self):
        cleaned_data = super().clean()
        
        # Get section data from POST
        section_titles = self.data.getlist('section_title[]', [])
        section_contents = self.data.getlist('section_content[]', [])
        section_priorities = self.data.getlist('section_priority[]', [])
        
        # Validate at least one section exists
        if not section_titles:
            raise ValidationError('At least one report section is required.')
        
        # Validate each section
        for i, title in enumerate(section_titles):
            if not title:
                raise ValidationError(f'Section {i+1} title is required.')
            
            if i < len(section_contents) and not section_contents[i]:
                raise ValidationError(f'Content is required for section {i+1}.')
            
            if i < len(section_priorities):
                try:
                    priority = int(section_priorities[i])
                    if priority < 1:
                        raise ValidationError(f'Priority for section {i+1} must be a positive number.')
                except (ValueError, TypeError):
                    raise ValidationError(f'Invalid priority value for section {i+1}.')
        
        return cleaned_data

class ReportSectionForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx,.xls,.xlsx'
            }
        )
    )

    class Meta:
        model = ReportSection
        fields = ['title', 'content', 'priority', 'seo_logs']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 6, 'class': 'summernote'}),
            'priority': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'seo_logs': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        if priority < 1:
            raise forms.ValidationError("Priority must be 1 or greater")
        return priority

    def save(self, commit=True):
        section = super().save(commit=commit)
        
        # Handle file uploads
        if self.cleaned_data.get('attachments'):
            for file in self.cleaned_data['attachments']:
                attachment = ReportAttachment(
                    report_section=section,
                    title=file.name,
                    file=file
                )
                if commit:
                    attachment.save()
        
        return section

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

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = field.title() 
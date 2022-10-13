from django import forms
from django.forms import ModelForm, Textarea, ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import DateInput
from . import models


class profileForm(ModelForm):
    class Meta:
        model = models.Profile
        #exclude = ('profileDesc', 'avatar',)
        fields = ['profileDesc', 'avatar']
        labels = {
            'profileDesc': ('Profile Description'), 'avatar': ('Avatar'),
        }

class userRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        model.is_staff = False
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']

# Profile Page Forms --------------------------------
# Verifies user changes in Account Details card
class profilePage_UserForm(ModelForm):
    class Meta:
        model = User
        model.is_staff = False
        fields = ['username', 'first_name', 'last_name',
                  'email']
# Verifies account changes in Account Details card
class profilePage_AccountForm(ModelForm):
    class Meta:
        model = models.Account
        fields = ['gender', 'dob']
# Verifies profile changes in Account Details card
class profilePage_ProfileForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ['profileDesc']
# Verifies address changes in Account Details card
class profilePage_AddressForm(ModelForm):
    class Meta:
        model = models.Address
        fields = ['street', 'city', 'state', 'country', 'zipcode']
# Verifies dependent changes on profile page
class profilePage_DependentForm(ModelForm):
    class Meta:
        model = models.Dependent
        fields = ['profile', 'type', 'name', 'dob', 'interests']
# Verify avatar image 
class profilePage_AvatarForm(ModelForm):
    # clean_image is a workaround to server-side
    # validate the verification image.
    def clean_image(self):
        avatarImg = self.cleaned_data['avatar']
        if avatarImg:
            # size measured in bytes
            if avatarImg.size > 6.5 * 1048578:
                raise ValidationError("Avatar image must be under 6.5 MB")
            avatarImgExt = avatarImg.name.split('.')[-1]
            allowedTypes = "apng, avif, gif jpeg, jpg, png, webp"
            if avatarImgExt in allowedTypes:
                return avatarImg
            raise ValidationError("Avatar image in the wrong format.")
        raise ValidationError("No avatar image uploaded.")
    class Meta:
        model = models.Profile
        fields = ['avatar']
        labels = {'avatar': ('Avatar Image')}
# Verify image in verification card
class profilePage_VerificationForm(ModelForm):
    # clean_image is a workaround to server-side
    # validate the verification image.
    def clean_image(self):
        verImg = self.cleaned_data['verification']
        if verImg:
            # size measured in bytes
            if verImg.size > 6.5 * 1048578:
                raise ValidationError("Verification image must be under 6.5 MB")
            verImgExt = verImg.name.split('.')[-1]
            allowedTypes = "apng, avif, gif jpeg, jpg, png, webp"
            if verImgExt in allowedTypes:
                return verImg
            raise ValidationError("Verification image in the wrong format.")
        raise ValidationError("No verification image uploaded.")
    class Meta:
        model = models.Profile
        fields = ['verification']
        labels = {'verification': ('Verification Document')}


class accountForm(ModelForm):
    class Meta:
        model = models.Account
        fields = ['gender', 'dob']
        labels = {
            'dob': ('D. O. B.'),
        }
        widgets = {
            'dob': DateInput(attrs={'type': 'date'})
        }

class supportForm(ModelForm):
    class Meta:
        model = models.Requestsupport
        fields = ['contact', 'name', 'type', 'details']
        labels = {
            'contact': ('Your Email or Phone'),
            'name': ('Name of the Issue'),
            'type': ('Support Category'),
            'details':  ('Please provide detail of the issue')
        }

class addressForm(ModelForm):
    class Meta:
        model = models.Address
        fields = ['street', 'state', 'country','zipcode','city']
        labels={
            'street':('Street/Building'),
            'state':('State'),
            'country':('Country'),
            'zipcode':('Zipcode'),
            'city':('City')
        }
        widgets = {
            'street': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "e.g. 123 Street"}),
            'state': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "e.g. CA"}),
            'country': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "e.g. USA"}),
            'zipcode': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "e.g. 12345"}),
            'city': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "e.g. San Francisco"}),
        }

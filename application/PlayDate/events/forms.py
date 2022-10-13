from django import forms
from django.forms import ModelForm, Textarea, widgets, ValidationError
from events.models import Event, Publicevent


class GroupEventForm(forms.Form):
    CATEGORY = (
        ('pets', 'Pets'),
        ('kids', 'Kids'),)
    # user = forms.CharField(label='User Name', max_length=200)
    name = forms.CharField(label='Event Name', max_length=200)
    category = forms.ChoiceField(choices=CATEGORY)
    street = forms.CharField(label='Street', max_length=200)
    city = forms.CharField(label='City', max_length=200)
    state = forms.CharField(label='State', max_length=200)
    country = forms.CharField(label='Country', max_length=200)
    zipcode = forms.CharField(label='Zipcode', max_length=200)

#public events
class PublicEventForm(ModelForm):
    class Meta:
        model = Publicevent
        fields = ['address', 'name', 'banner', 'category']
        labels = {'address': ('Address'),
                  'name': ('Event Name'), 'banner': ('banner'), 'category': ('category')}

#user events
class eventForm(ModelForm):
    # clean_image is a workaround to server-side
    # validate the banner image.
    def clean_image(self):
        bannerImage = self.cleaned_data['banner']
        if bannerImage:
            # size measured in bytes
            if bannerImage.size > 6.5 * 1048578:
                raise ValidationError("Banner image must be under 6.5 MB")
            bannerImageExt = bannerImage.name.split('.')[-1]
            allowedTypes = "apng, avif, gif jpeg, jpg, png, webp"
            if bannerImageExt in allowedTypes:
                return bannerImage
            raise ValidationError("Banner image in the wrong format.")
        raise ValidationError("No banner image uploaded.")

    class Meta:
        model = Event
        fields=['name', 'banner', 'category', 'desc','datetime']
        labels={'name':('Event Name'),'banner':('Image'),'category':('category'),'desc':('Description'),'datetime':('datetime')}
        exclude = ()
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "Kyle's 12th Birthday Party!"}),
            'category': forms.TextInput(attrs={'style': 'width: 25rem;', 'placeholder': "e.g. pets or kids"}),
            'desc': forms.TextInput(attrs={'style': 'width: 25rem;' 'height:100px', 'placeholder': "add event description..."}),
            'datetime': forms.DateInput(attrs={'style': 'width: 25rem;','type': 'date'}),
        }
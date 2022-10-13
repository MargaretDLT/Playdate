from django.contrib import admin
from home.models import Profile


class profileAdministration(admin.ModelAdmin):
    list_display = ('get_profile', 'profileID', 'is_verified',)
    search_fields = ['profileID__id',
                     'profileID__username', 'profileID__email']

    @admin.display(description='Profile ID', ordering='profileID_id')
    def get_profile(self, obj):
        return obj.profileID.id

    @admin.display(description='email', )
    def get_email(self, obj):
        return obj.profileID.email


admin.site.register(Profile, profileAdministration)

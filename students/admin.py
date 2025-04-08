from django.contrib import admin
from .models import studentregistermodel,ApplicantDetails,ResidentialAddress,RouteSelection


class registermember(admin.ModelAdmin):
  list_display = ("name", "email", "mobile","status")  
admin.site.register(studentregistermodel, registermember)



admin.site.register(ApplicantDetails)
admin.site.register(ResidentialAddress)


class routestable(admin.ModelAdmin):

  list_display = ('application_number','applicant','route')
admin.site.register(RouteSelection,routestable)  






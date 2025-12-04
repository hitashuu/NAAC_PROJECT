from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Work_Detail,Personal_Detail,Bank_Detail,Experience_Detail,Contact_Detail,Patent,PHD_Awarded,Paper_Publication,Awards,Books,Books_Conference,CSV_Download,Head

from import_export.admin import ExportActionMixin


class User_Info_Admin(ExportActionMixin, admin.ModelAdmin):
    exclude = ['password']

# Register your models here.

admin.site.register(User)
admin.site.register(Personal_Detail)
admin.site.register(Work_Detail)
admin.site.register(Bank_Detail)
admin.site.register(Experience_Detail)
admin.site.register(Patent)
admin.site.register(PHD_Awarded)
admin.site.register(Paper_Publication)
admin.site.register(Awards)
admin.site.register(Books)
admin.site.register(Books_Conference)
admin.site.register(CSV_Download)

admin.site.register(Head)




from django.contrib import admin
from .models import *
# Register your models here.

class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'internship')

admin.site.register(Skill)
admin.site.register(SkillUser)
admin.site.register(Internship)
admin.site.register(SkillInternship)
admin.site.register(Question)
admin.site.register(Test, TestAdmin)
admin.site.register(UserTestResult)
admin.site.register(UserTestQuestionResult)

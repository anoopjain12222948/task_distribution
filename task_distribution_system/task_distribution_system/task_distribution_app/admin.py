from django.contrib import admin

from .models import Resource, Project, Task, TaskResourceMapping

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'skills','busy_days_count')
    
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date')
    
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'start_date', 'end_date', 'skill_required', 'resource', 'status', 'priority')

class TaskResourceMappingAdmin(admin.ModelAdmin):
    list_display = ('task', 'project', 'start_date', 'end_date', 'resource')

admin.site.register(Resource, ResourceAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskResourceMapping, TaskResourceMappingAdmin)

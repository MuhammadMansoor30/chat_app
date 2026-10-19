from django.contrib import admin
from chat.models import User, Role, Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import SimpleListFilter
from simple_history.admin import SimpleHistoryAdmin

class RoleFilter(SimpleListFilter):
    title = 'role'
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return Role.objects.values_list('id', 'name')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(roles__id__in=[self.value()])

class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin):
    list_display = ('username', 'created_at', 'updated_at')
    readonly_fields = ['is_staff']
    search_fields = ['username', 'full_name', 'cnic']
    list_filter = ('deleted', RoleFilter)
    fieldsets = ()
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'username','email','password1', 'password2'),
        }),
    )
    filter_horizontal=[]
    raw_id_fields = ('created_by', 'updated_by')

class RoleAdmin(SimpleHistoryAdmin):
    search_fields = ['code_name', 'name']
    raw_id_fields = ('created_by', 'updated_by')
    list_filter = ('deleted',)

class PermissionAdmin(admin.ModelAdmin):
    search_fields = ['code_name']
    list_display = ('name', 'code_name', 'description')

# Register your models here.

admin.site.site_header = "Chat App"
admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission, PermissionAdmin)

from django.contrib import admin
from chat.models import User, Role, Permission, Conversation, Message, Organization
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
    raw_id_fields = ('organization', 'created_by', 'updated_by')

class RoleAdmin(SimpleHistoryAdmin):
    search_fields = ['code_name', 'name']
    raw_id_fields = ('created_by', 'updated_by')
    list_filter = ('deleted',)

class PermissionAdmin(admin.ModelAdmin):
    search_fields = ['code_name']
    list_display = ('name', 'code_name', 'description')

class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'created_at')
    raw_id_fields = ('created_by', 'updated_by')

class ConversationAdmin(admin.ModelAdmin):
    raw_id_fields = ('organization', 'created_by', 'updated_by')

class MessageAdmin(admin.ModelAdmin):
    search_fields = ['message', 'sender__username']
    list_display = ('message', 'sender__username', 'created_at')
    raw_id_fields = ('conversation', 'created_by', 'updated_by')

# Register your models here.

admin.site.site_header = "Chat App"
admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Organization, OrganizationAdmin)

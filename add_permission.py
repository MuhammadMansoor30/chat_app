import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'hms.settings')

import django
django.setup()

from chat.models import Permission

all_permission = [
    {"name": "Read Role", "code_name": "role_read", "description": "User can read all roles"},
    {"name": "Create Role", "code_name": "role_create", "description": "User can create roles"},
    {"name": "Update Role", "code_name": "role_update", "description": "User can udpate roles"},
    {"name": "Delete Role", "code_name": "role_delete", "description": "User can delete roles"},
    {"name": "Read Organization", "code_name": "organization_read", "description": "User can read all organization"},
    {"name": "Create Organization", "code_name": "organization_create", "description": "User can create an organization"},
    {"name": "Update Organization", "code_name": "organization_update", "description": "User can update an organization"},
    {"name": "Delete Organization", "code_name": "organization_delete", "description": "User can delete an organization"},
]

def add_permission():
    for perm_dict in all_permission:
        try:
            Permission.objects.get(code_name=perm_dict['code_name'])
        except Permission.DoesNotExist:
            Permission.objects.create(
                name=perm_dict['name'],
                code_name=perm_dict['code_name'],
                description=perm_dict['description'],
            )


if __name__ == '__main__':
    print("Adding permissions to HMS...")
    add_permission()


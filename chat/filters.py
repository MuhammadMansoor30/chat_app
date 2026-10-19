import django_filters as filters
from chat.models import User, Role, Organization

class OrganizationFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Organization
        fields = ['name']

class RoleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Role
        fields = ['name']
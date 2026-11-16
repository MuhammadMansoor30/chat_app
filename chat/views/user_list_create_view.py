from chat.decorator import permission_required
from chat.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from chat.models import User
from rest_framework.generics import ListAPIView
from chat.util import CustomPagination

class UserListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = UserSerializer

    @permission_required(['user_read'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        return User.objects.filter(deleted=False, organization = self.request.user.organization).exclude(id=self.request.user.id).order_by("-created_at")

from chat.decorator import permission_required
from chat.serializers import ConversationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Conversation
from rest_framework.generics import ListAPIView
from chat.util import CustomPagination
from datetime import datetime

class ConversationListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    serializer_class = ConversationSerializer

    @permission_required(['conversation_read'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        
    def get_queryset(self):
        return Conversation.objects.filter(participants = self.request.user, deleted=False).order_by("-updated_at")
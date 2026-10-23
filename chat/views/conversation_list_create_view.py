from rest_framework.views import APIView
from chat.decorator import permission_required
from chat.serializers import ConversationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chat.models import Conversation
from chat.util import CustomPagination
from datetime import datetime

class ConversationListView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ConversationSerializer

    @permission_required(['conversation_read'])
    def get(self, request, *args, **kwargs):
        conversations = Conversation.objects.filter(organization = request.user.organization, participants = self.request.user, deleted=False).order_by("-updated_at")
        serialzier = self.serializer_class(conversations, many=True)

        return Response(serialzier.data, status=status.HTTP_200_OK)
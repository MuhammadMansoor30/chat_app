from rest_framework.views import APIView
from chat.decorator import permission_required
from chat.serializers import ConversationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from chat.models import Conversation, User

class ConversationListView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = ConversationSerializer

    @permission_required(['conversation_read'])
    def get(self, request, *args, **kwargs):
        conversations = Conversation.objects.filter(organization = request.user.organization, participants = self.request.user, deleted=False).order_by("-updated_at")
        serialzier = self.serializer_class(conversations, many=True)

        return Response(serialzier.data, status=status.HTTP_200_OK)

    @permission_required(['conversation_create'])
    def post(self, request, *args, **kwargs):
        participants = request.data.get('participants')
        group_name = request.data.get('group_name', None)

        users = User.objects.filter(deleted=False, id__in=participants)

        if len(users) > 1:
            conversation = Conversation.objects.filter(participants__in=users).annotate(num_participants=Count('participants')).filter(num_participants=len(users)).first()

            serializer = self.serializer_class(data = request.data)
            if not conversation:
                if serializer.is_valid():
                    serializer.save(created_by=request.user, organization=request.user.organization)
                else:
                    print(serializer.error_messages)

                return Response({"msg": "Conversation Created Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                conversation = self.serializer_class(conversation).data
                return Response({"msg": "Conversation Already Exists", "data": conversation}, status=status.HTTP_201_CREATED)

        else:
            return Response({"msg": "Please Select a contact to start conversation with"}, status=status.HTTP_400_BAD_REQUEST)


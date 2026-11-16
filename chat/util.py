from rest_framework import pagination
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from channels.layers import get_channel_layer
from rest_framework_simplejwt.tokens import RefreshToken
from chat.models import User, Conversation, Message
from channels.db import database_sync_to_async
from datetime import datetime

class CustomPagination(pagination.PageNumberPagination):
    
    def get_from(self):
        return int((self.page.paginator.per_page * self.page.number) - self.page.paginator.per_page + 1)

    def get_to(self):
        return self.get_from() + int(len(self.page.object_list)) - 1

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'per_page': self.page.paginator.per_page,
            'from': self.get_from(),
            'to': self.get_to(),
            'results': data
        })

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_access_cookies(response, access_token):
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_ACCESS_COOKIE'],
        value=access_token,
        expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )

def set_refresh_cookies(response, refresh_token):
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE'],
        value=refresh_token,
        expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )


def unset_cookies(response):
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_ACCESS_COOKIE'])
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE'])
    response.delete_cookie(settings.CSRF_COOKIE_NAME)

def get_permissions_from_roles(roles):
    permissions = []

    for role in roles:
        role_permissions = role.permissions.all()
        for permission in role_permissions:
            permissions.append(permission.code_name)

    return permissions


ALLOWED_CONTENT_TYPES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",   
    "application/vnd.ms-excel",                                               
    "application/x-compressed",        
    "application/x-zip-compressed",
    "application/pdf"                                         
]

def send_message_sync(sender_id, recipients, group_name, content, content_type, user, data=None):
    # content = content.strip()
    if not content:
        raise ValueError("No Content Provided")

    sender = User.objects.get(deleted=False, id=sender_id)
    recipient = User.objects.filter(deleted=False, id__in=recipients)
        

    with transaction.atomic():
        # conversation = Conversation.objects.filter(participants__in=[sender, recipient]).distinct().first()    
        conversation = Conversation.objects.filter(participants__in=[sender, *recipient])

        if not group_name:
            conversation = conversation.annotate(num_participants=Count('participants', distinct=True)).filter(num_participants=2).first()
        else:
            conversation = conversation.filter(group_name=group_name).annotate(num_participants=Count('participants', distinct=True)).filter(num_participants__gte=2).first()

        if conversation is not None:
            conversation.last_message_time = datetime.now()
            conversation.last_message = content
            conversation.last_message_by = sender
            conversation.save()
            
        else:
            conversation = Conversation.objects.create(organization=user.organization, last_message_time=datetime.now(), last_message=content, last_message_by=sender)
            conversation.participants.add(sender, recipient)
            conversation.save()


        if content_type == "text":
            message = Message.objects.create(conversation=conversation, message=content, sender=sender, created_by=user, status=data['status'])
        elif "image" in content_type:
            message = Message.objects.create(conversation=conversation, attachment=content, sender=sender, created_by=user, status=data['status'], type=Message.PICTURE)
        elif "video" in content_type:
            message = Message.objects.create(conversation=conversation, attachment=content, sender=sender, created_by=user, status=data['status'], type=Message.VIDEO)
        elif content_type in ALLOWED_CONTENT_TYPES:
            message = Message.objects.create(conversation=conversation, attachment=content, sender=sender, created_by=user, status=data['status'], type=Message.DOCUMENT)
        elif "audio" in content_type:
            message = Message.objects.create(conversation=conversation, attachment=content, sender=sender, created_by=user, status=data['status'], type=Message.VOICE)

    return message

@database_sync_to_async
def send_message(sender_id, recipient_id, group_name, content, content_type, user, data=None):
    return send_message_sync(sender_id, recipient_id, group_name, content, content_type, user, data)

@database_sync_to_async
def change_user_status(user_id, status):
    User.objects.filter(id=user_id).update(is_online=status, last_seen=None if not status else timezone.now())
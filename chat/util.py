from rest_framework import pagination
from rest_framework.response import Response
from django.conf import settings
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

@database_sync_to_async
def send_message(sender_id, recipient_id, content, user):
    content = content.strip()
    
    if not content:
        raise ValueError("No Content Provided")

    sender = User.objects.get(deleted=False, id=sender_id)
    recipient = User.objects.get(deleted=False, id=recipient_id)

    conversation = Conversation.objects.filter(participants__in=[sender, recipient]).distinct().first()
    if conversation is not None:
        conversation.last_message_time = datetime.now()
        conversation.last_message = content
        conversation.save()
        
    else:
        conversation = Conversation.objects.create(organization=user.organization, last_message_time=datetime.now(), last_message=content)
        conversation.participants.add(sender, recipient)
        conversation.save()

    message = Message.objects.create(conversation=conversation, message=content, sender=sender, created_by=user)

    return message
    
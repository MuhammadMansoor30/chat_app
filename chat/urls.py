from django.urls import path
from chat.consumer import ChatConsumer
from chat import views

urlpatterns = [
    path("login",                           views.LoginView.as_view()),
    path("logout",                          views.LogoutView.as_view()),
    path("refresh",                         views.RefreshView.as_view()),
    path("current",                         views.CurrentUserView.as_view()),
    path("role/",                           views.RoleListView.as_view()),
    path("role/<int:pk>",                   views.RoleDetailView.as_view()),
    path("permission/",                     views.PermissionListView.as_view()),
    path("organization/",                   views.OrganizationListView.as_view()),
    path("organization/<int:pk>",           views.OrganizationDetailView.as_view()),
    path("conversation/",                   views.ConversationListView.as_view()),
    path("messages/",                       views.MessageListView.as_view()),

]

websocket_pattern = [
    path("ws/chat/", ChatConsumer.as_asgi()),
]

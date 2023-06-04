from allauth.account.views import LogoutView, LoginView
from django.urls import path

from board.views import *

urlpatterns = [
    path('', BoardHome.as_view(), name='home'),
    path('board/', UserBoard.as_view(), name='user_board'),
    path('responses/', UserResponses.as_view(), name='user_responses'),
    path('response/<int:comment_pk>/delete/', ResponseDelete.as_view(), name='delete_comment'),
    path('send_email/<int:comment_pk>/', send_email_to_owner, name='send_email_to_owner'),
    path('about/', about, name='about'),
    path('create/', AnnouncementCreate.as_view(), name='announcement_create'),
    path('update/<slug:ann_slug>', AnnouncementUpdate.as_view(), name='update'),
    path('announcement/<slug:ann_slug>', ShowAnnouncement.as_view(), name='announcement'),
    path('add_comment/', AddComment.as_view(), name='add_comment'),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/signup/', CustomSignup.as_view(), name='signup'),
    path('newsletter/', Newsletter.as_view(), name='newsletter'),
]

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.dispatch import receiver

from board.models import Comment


@receiver(post_save, sender=Comment)
def send_comment_notification(instance, **kwargs):
    created = kwargs['created']
    if created:
        comment = instance
        announcement = comment.announcement
        owner = announcement.author
        subject = 'NEW Comment'
        message = render_to_string('board/comment_notification_email.html',
                                   {'owner': owner, 'comment': comment, 'announcement': announcement})
        plain_message = strip_tags(message)
        send_mail(subject, plain_message, 'your_email@example.com', [owner.email], html_message=message)

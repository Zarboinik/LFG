from allauth.account.views import SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from board.forms import AnnouncementForm, NewsletterForm
from board.models import *
from board.utils import *


class BoardHome(MenuTitleMixin, ListView):
    paginate_by = 3
    model = Announcement
    template_name = 'board/index.html'
    context_object_name = 'announcements'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Доска Объявлений')
        return dict(list(context.items()) + list(c_def.items()))


class UserBoard(LoginRequiredMixin, MenuTitleMixin, ListView):
    paginate_by = 3
    model = Announcement
    template_name = 'board/user_board.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        author = self.request.user
        return Announcement.objects.filter(author=author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Мои Объявления')
        return dict(list(context.items()) + list(c_def.items()))


class UserResponses(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'board/user_responses.html'
    context_object_name = 'comments_dict'
    paginate_by = 3

    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(author=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        announcements = context['object_list']

        # Создаем словарь, где ключом будет объявление, а значением - список комментариев
        comments_dict = {announcement: announcement.comments.all() for announcement in announcements}

        context['comments_dict'] = comments_dict
        return context


class ResponseDelete(View):
    def post(self, request, comment_pk):
        comment = Comment.objects.get(pk=comment_pk)
        comment.delete()
        return redirect('user_responses')


def send_email_to_owner(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    owner_email = comment.announcement.author.email
    subject = 'Новое сообщение откликнулись'
    message = 'Здравствуйте,\n\nУ вас есть отклик на ваше сообщение:\n\n{}'.format(comment.text)
    sender_email = '{{your_email@example.com}}'

    send_mail(subject, message, sender_email, [owner_email])
    return HttpResponse('Email отправлен владельцу комментария')


def about(request):
    user_menu = menu.copy()
    user_menu.pop(1)
    return render(request, 'board/about.html', {'menu': user_menu, 'title': 'О сайте'})


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


class AnnouncementCreate(MenuTitleMixin, LoginRequiredMixin, CreateView):
    form_class = AnnouncementForm
    template_name = 'board/announcement_create.html'
    login_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Создания объявления')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AnnouncementUpdate(LoginRequiredMixin, UpdateView):
    model = Announcement
    template_name = 'board/announcement_edit.html'
    fields = ['title', 'text', 'category', 'content']
    slug_url_kwarg = 'ann_slug'
    context_object_name = 'announcement'

    def get_success_url(self):
        return reverse_lazy('announcement', kwargs={'ann_slug': self.object.slug})

    def dispatch(self, request, *args, **kwargs):
        announcement = self.get_object()

        if announcement.author != self.request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class ShowAnnouncement(DetailView):
    model = Announcement
    template_name = 'board/announcement.html'
    slug_url_kwarg = 'ann_slug'
    context_object_name = 'announcement'
    comments_per_page = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        announcement = self.get_object()
        comments = announcement.get_comments()
        context['comments'] = comments
        self.add_pagination_context(context, comments)
        self.add_user_menu_context(context)
        return context

    def add_pagination_context(self, context, comments):
        paginator = Paginator(comments, self.comments_per_page)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['comments'] = page_obj
        context['paginator'] = paginator
        context['page_obj'] = page_obj

    def add_user_menu_context(self, context):
        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu
        context['title'] = 'Поиск Группы'


class AddComment(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request):
        announcement_id = request.POST.get('announcement_id')
        text = request.POST.get('text')
        announcement = get_object_or_404(Announcement, id=announcement_id)
        Comment.objects.create(announcement=announcement, author=request.user, text=text)
        return redirect('announcement', ann_slug=announcement.slug)


def send_newsletter(message):
    subscribers = User.objects.all()
    recipient_list = [subscriber.email for subscriber in subscribers]
    send_mail('Новости вашего проекта', message, 'your_email@example.com', recipient_list)


class Newsletter(View):
    template_name = 'board/newsletter.html'

    def get(self, request):
        form = NewsletterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NewsletterForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            send_newsletter(message)
            return redirect('home')
        else:
            return render(request, self.template_name, {'form': form})


# django-allauth
class CustomSignup(SignupView):
    template_name = 'registration/signup.html'


signup = CustomSignup.as_view()

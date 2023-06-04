import uuid

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Announcement(models.Model):
    TYPE = (
        ('tanks', 'Танки'),
        ('heals', 'Хилы'),
        ('dd', 'ДД'),
        ('merchants', 'Торговцы'),
        ('guildmaster', 'Гилдмастеры'),
        ('questgivers', 'Квестгиверы'),
        ('blacksmiths', 'Кузнецы'),
        ('leatherworkers', 'Кожевники'),
        ('alchemists', 'Зельевары'),
        ('spellmasters', 'Мастера заклинаний'),
    )
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст объявления')
    category = models.CharField(max_length=20, choices=TYPE, default='tanks', verbose_name='Категория')
    content = models.FileField(upload_to='board_content/%Y/%m/%d/', null=True, blank=True,
                               verbose_name='Медиа')  # Поле для хранения контента
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Объявления'
        verbose_name_plural = 'Объявления'
        ordering = ['-time_create', 'title']

    def __str__(self):
        return self.title

    def get_category_display(self):
        return next((v for k, v in self.TYPE if k == self.category), None)

    def get_absolute_url(self):
        return reverse('announcement', kwargs={'ann_slug': self.slug})

    def get_update_url(self):
        return reverse('update', kwargs={'ann_slug': self.slug})

    def generate_slug(self):
        unique_id = str(uuid.uuid4())[:12]  # Генерация уникального идентификатора
        slug = slugify(f'{self.title} {unique_id}')
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

    def get_comments(self):
        return self.comments.all()


class Comment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='comments',
                                     verbose_name='Объявление')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-time_create']

    def __str__(self):
        return self.text

    def delete_comment(self):
        self.delete()

    def get_delete_url(self):
        return reverse('delete_comment', args=[self.pk])

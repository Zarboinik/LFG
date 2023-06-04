menu = [
    {'title': 'Доска объявлений', 'url_name': 'home'},
    {'title': 'Добавить объявление', 'url_name': 'announcement_create'},
    {'title': 'О сайте', 'url_name': 'about'},
    {'title': 'Рассылка новостей', 'url_name': 'newsletter'},
]


class MenuTitleMixin:
    def get_user_context(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
        context['menu'] = user_menu
        return context

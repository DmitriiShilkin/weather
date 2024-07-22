from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Count
from django.shortcuts import render
import asyncio

from django.views.generic import CreateView, ListView

from .models import City, History
from .services import get_weather, get_context_data


# Представление для стартовой страницы
class IndexView(CreateView):
    model = City
    fields = '__all__'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        last_viewed = None
        if self.request.user.is_authenticated:
            last_viewed = History.objects.filter(user_id=self.request.user).last()

        cities = cache.get('cities')
        if not cities:
            cities = City.objects.all()
            cache.set('cities', cities, 60 * 15)  # Кэшируем на 15 минут

        cities_names = cache.get('cities_names')
        if not cities_names:
            cities_names = list(cities.values_list('name_ascii', 'country', 'region'))
            cache.set('cities_names', cities_names, 60 * 15)  # Кэшируем на 15 минут

        context['cities_names'] = cities_names
        context['last_viewed'] = last_viewed
        return context

    def post(self, request, *args, **kwargs):
        if 'city_name' in request.POST:
            city = None

            cities = cache.get('cities')
            if not cities:
                cities = City.objects.all()
                cache.set('cities', cities, 60 * 15)  # Кэшируем на 15 минут

            cities_names = cache.get('cities_names')
            if not cities_names:
                cities_names = list(cities.values_list('name_ascii', 'country', 'region'))
                cache.set('cities_names', cities_names, 60 * 15)  # Кэшируем на 15 минут

            try:
                name, country, region = eval(request.POST['city_name'])
                city = cities.filter(name_ascii=name, country=country, region=region).first()
            except NameError:
                pass
            except SyntaxError:
                pass

            if city:
                result = get_context_data(
                    asyncio.run(
                        get_weather(city.latitude, city.longitude)
                    )
                )
                data = {
                    'city': city,
                    'result': result,
                    'cities_names': cities_names,
                }
                if request.user.is_authenticated:
                    History.objects.create(city=city, user=request.user)
                return render(self.request, 'index.html', context=data)

        return render(self.request, 'city/invalid_name.html')


# Представление для повторной отправки запроса
def repeat_view(request, cname):
    cities = City.objects.all()
    name, country, region = cname.replace(' (', '/').replace(', ', '/').replace(')', '').split('/')
    city = cities.filter(name=name, country=country, region=region).first()
    cities_names = cities.values_list('name_ascii', 'country', 'region')
    result = get_context_data(
        asyncio.run(
            get_weather(city.latitude, city.longitude)
        )
    )
    data = {
        'city': city,
        'result': result,
        'cities_names': cities_names,
    }
    if request.user.is_authenticated:
        History.objects.create(city=city, user=request.user)
    return render(request, 'index.html', context=data)


# Представление для просмотра истории запросов
class HistoryListView(PermissionRequiredMixin, ListView):
    model = History
    context_object_name = 'cities'
    template_name = 'city/history.html'
    ordering = 'city__name'
    permission_required = ('city.view_history',)
    raise_exception = True
    paginate_by = 10

    def get_queryset(self):
        return History.objects.filter(user_id=self.request.user).\
            values('city__name', 'city__country', 'city__region').\
            annotate(count=Count('city')).order_by(self.ordering)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.db.models import Count

from app.models import SearchHistory


@api_view(['GET'])
def search_history_api(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2 and auth[0].lower() == "basic":
            import base64
            username, password = base64.b64decode(auth[1]).decode('utf-8').split(':')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                city_stats = SearchHistory.objects.filter(user=user) \
                    .values('city__name') \
                    .annotate(count=Count('id')) \
                    .order_by('-count')
                return Response({'stats': list(city_stats)})

    return Response(
        {'detail': 'Неверные логин или пароль.'},
        status=status.HTTP_401_UNAUTHORIZED
    )

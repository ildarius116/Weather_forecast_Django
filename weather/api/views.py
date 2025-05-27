from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from app.models import SearchHistory

from .schema import search_history_docs

@search_history_docs
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def search_history_api(request):
    city_stats = SearchHistory.objects.filter(user=request.user) \
        .values('city__name') \
        .annotate(count=Count('id')) \
        .order_by('-count')
    return Response({'stats': list(city_stats)})

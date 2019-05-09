from django.contrib.auth.models import User, Group
from django.utils import timezone, dateformat
from django.db.models.functions import TruncMonth
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from internal.models import Link, Event
from internal.serializers import LinkSerializer, EventSerializer
from internal.permissions import IsLinkCreator, HasEventPermission
from datetime import datetime, timedelta
from dateutil import parser
import pdb

class LinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    serializer_class = LinkSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsLinkCreator)

    def get_queryset(self):
      """
      Given a username parameter, returns only the links that the
      specified user created
      """
      queryset = Link.objects.all()
      username = self.request.query_params.get('username', None)
      if username is not None:
          queryset = queryset.filter(creator__username=username)
      return queryset

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (AllowAny, HasEventPermission)
    # TODO(TrinaKat): test all this date filtering

    def filter_by_date_range(self, queryset):
      """
      Given optional start/end parameters, returns events in the specified
      custom time period.
      """
      start = self.request.query_params.get('start', None)
      try:
        if start is not None:
          start = parser.parse(start)
      except:
        start = None

      end = self.request.query_params.get('end', None)
      try:
        if end is not None:
          end = parser.parse(end).replace(hour=23, minute=59, second=59)
      except:
        end = None

      if start is not None or end is not None:
        if start is not None and end is not None:
          queryset = queryset.filter(time__range=[start, end])
        elif start:
          queryset = queryset.filter(time__gte=start)
        else:
          queryset = queryset.filter(time__lte=end)

      return queryset

    def filter_by_time(self, queryset):
      # TODO: @reviewer(s) do we want to specify date ranges like:
      # week = from 7 days before today, OR monday to monday
      # month = from 30 days before today, OR month of may
      # or we could do both
      # for data visualization, would want the latter options
      # for user/influencer benefits, they may want the former options
      # I'll just do both and y'all can decide when u review if we hate this
      """
      Given an optional time parameter, return events in the specified time
      period.
      """
      today = timezone.now()
      date = today.date()
      month = dateformat.format(today, 'm')
      year = dateformat.format(today, 'Y')
      last_monday = today - timedelta(days=today.weekday())
      this_monday = today + timedelta(days=-today.weekday(), weeks=1)
      last_7_days = today.date() - timedelta(days=7)
      last_30_days = today.date() - timedelta(days=30)
      last_90_days = today.date() - timedelta(days=90)

      time = self.request.query_params.get('time', None)
      if time is not None:
        time = time.lower()
        return {
          'latest': queryset.order_by('-time')[:1],
          'today': queryset.filter(time__date=date),
          'week': queryset.filter(time__range=[last_monday, this_monday]),
          'month': queryset.filter(time__year=year, time__month=month),
          '7days': queryset.filter(time__range=[last_7_days, today]),
          '30days': queryset.filter(time__range=[last_30_days, today]),
          '90days': queryset.filter(time__range=[last_90_days, today]),
        }.get(time, self.filter_by_date_range(queryset))
      return self.filter_by_date_range(queryset)

    def get_queryset(self):
      """
      Given optional filtering parameters, return any corresponding events.
      """
      queryset = Event.objects.all()
      link_id = self.request.query_params.get('link', None)
      username = self.request.query_params.get('username', None)
      if link_id is not None:
        queryset = queryset.filter(link=link_id)
      elif username is not None:
        queryset = queryset.filter(link__creator__username=username)

      queryset = self.filter_by_time(queryset)
      return queryset

    @action(detail=False, methods=['get'], url_path='stats', name='Event Stats')
    def get_event_stats(self, request):
      """
      Given a method parameter, returns event data in the specified format. Can
      return 'count' statistics or the original Event data.
      TODO: stats by device type, geographic region, time of day/week
      """
      queryset = self.get_queryset()
      method = self.request.query_params.get('method', None)
      if method is not None and method.lower() == 'count':
        return Response({ 'stat': queryset.count() })
      serializer = self.serializer_class(queryset, many=True)
      return Response(serializer.data)

    def create(self, request):
      """
      Creates an event for the specified link_id. Admins may specify a time
      parameter.
      """
      link_id = self.request.POST.get('link', None)
      time = self.request.POST.get('time', None)
      try:
        if time is not None:
          time = parser.parse(time)
      except:
        time = None

      if link_id is not None:
        event = Event.objects.create(link_id=link_id)
        if request.user.is_superuser and time is not None:
          event = Event.objects.create(link_id=link_id, time=time)
        event.save()
        serializer = EventSerializer(event)
        return Response(serializer.data)
      return Response(status=status.HTTP_400_BAD_REQUEST)

    # Disable PUT/DELETE endpoints.
    def update(self, request, pk=None):
      return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def partial_update(self, request, pk=None):
      return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def destroy(self, request, pk=None):
      return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

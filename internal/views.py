from django.contrib.auth.models import User, Group
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.http import JsonResponse
from django.utils import timezone, dateformat
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from internal.models import Link, Event, Preference
from internal.permissions import IsOwner, HasEventPermission
from internal.serializers import LinkSerializer, EventSerializer, PreferenceSerializer, UserSerializer
from datetime import datetime, timedelta
from dateutil import parser
import pdb

def error_404(request, *args, **argv):
    return JsonResponse({
        'details': 'invalid URL - check OPTION /api'
    }, status=404)

def error_500(request, *args, **argv):
    return JsonResponse({
        'details': 'server failure'
    }, status=500)

class LinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    serializer_class = LinkSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)

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

    def filter_by_id(self):
      """
      Given an optional link or username parameter, return events for the
      specified link(s).
      """
      queryset = Event.objects.all()
      link_id = self.request.query_params.get('link', None)
      username = self.request.query_params.get('username', None)
      if link_id is not None:
        queryset = queryset.filter(link=link_id)
      elif username is not None:
        queryset = queryset.filter(link__creator__username=username)
      return queryset

    def get_queryset(self):
      """
      Given optional filtering parameters, return any corresponding events.
      """
      queryset = self.filter_by_id()
      queryset = self.filter_by_time(queryset)
      return queryset

    @action(detail=False, methods=['get'], url_path='stats', name='Event Stats')
    def get_event_stats(self, request):
      """
      Given a method parameter, returns event data in the specified format. Can
      return 'count' statistics or the original Event data.
      TODO: figure out return format
      TODO: restrict date range for daily/weekly/monthly/yearly data?
      TODO: stats by device type, geographic region, time of day/week
      """
      output = []
      queryset = self.filter_by_id()
      time = self.request.query_params.get('time', None)
      method = self.request.query_params.get('method', None)
      if time is None:
        queryset = self.filter_by_date_range(queryset)
        if method is not None and method.lower() == 'count':
          return Response({ 'count': queryset.count() })
        serializer = self.serializer_class(queryset, many=True)
        output = serializer.data
      else:
        time = time.lower()
        if time in ['daily', 'weekly', 'monthly', 'yearly']:
          queryset = {
            'daily': queryset.annotate(period=TruncDay('time')),
            'weekly': queryset.annotate(period=TruncWeek('time')),
            'monthly': queryset.annotate(period=TruncMonth('time')),
            'yearly': queryset.annotate(period=TruncYear('time')),
          }.get(time).order_by('period')

          # TODO: there is probably a better way to do this query
          # Do we even want this query

          # Creates Event model from data cols
          # queryset = queryset \
          #           .values('period') \
          #           .annotate(ids=ArrayAgg('id'), links=ArrayAgg('link'), times=ArrayAgg('time')) \
          #           .values('period', 'ids', 'links', 'times')
          # for q in queryset:
          #   data = list(EventSerializer(Event(id=id, link_id=link, time=time), many=False).data \
          #     for id, link, time in zip(q['ids'], q['links'], q['times']))
          #   output.append({ 'period': q['period'], 'count': len(data), 'events': data})

          # Fetches Event entry by primary key
          queryset = queryset \
                    .values('period') \
                    .annotate(event_ids=ArrayAgg('id')) \
                    .values('period', 'event_ids')
          for q in queryset:
            data = list(EventSerializer(Event.objects.get(pk=id), many=False).data for id in q['event_ids'])
            output.append({ 'period': q['period'], 'count': len(data), 'events': data })

          # Just returns array of timestamps per period
          # output = queryset \
          #         .values('period') \
          #         .annotate(times=ArrayAgg('time')) \
          #         .values('period', 'times')
        else:
          queryset = self.filter_by_time(queryset)
          if method is not None and method.lower() == 'count':
            return Response({ 'count': queryset.count() })
          serializer = self.serializer_class(queryset, many=True)
          output = serializer.data

      return Response(output)

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

class PreferenceViewSet(mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows preferences to be viewed or edited.
    """
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def list(self, request):
        """
        Returns user's preferences
        """
        queryset = Preference.objects.get(user=request.user)
        serializer = PreferenceSerializer(queryset)
        return Response(serializer.data)

class UserViewSet(mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to update name and email.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def list(self, request):
        """
        Returns user's info
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

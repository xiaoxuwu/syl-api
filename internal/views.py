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

def user_exists(username):
    queryset = User.objects.filter(username=username)
    return len(queryset) == 1

class LinkViewSet(mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    queryset = Link.objects.all()
    serializer_class = LinkSerializer(many=True)
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)

    def list(self, request):
      """
      Given a username parameter, returns only the links that the
      specified user created
      """
      queryset = Link.objects.all()
      username = request.query_params.get('username', None)
      if username is not None:
        if not user_exists(username):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = Link.objects.filter(creator__username=username)

      serializer = LinkSerializer(queryset, many=True)
      return Response(serializer.data)

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (AllowAny, IsOwner, HasEventPermission)
    
    def parse_date(self, date):
        try:
            if date is not None:
                return parser.parse(date)
        except:
            return None

    def parse_int(self, num):
        try:
            if num is not None:
                return int(num)
        except:
            return None

    def filter_by_date_range(self, queryset):
        """
        Given optional start/end parameters, returns events in the specified 
        custom time period.
        """
        start = self.request.query_params.get('start', None)
        start = self.parse_date(start)
        end = self.request.query_params.get('end', None)
        end = self.parse_date(end)
        if end is not None:
            end = end.replace(hour=23, minute=59, second=59)

        if start is not None or end is not None:
            if start is not None and end is not None:
                return queryset.filter(time__range=[start, end])
            elif start:
                return queryset.filter(time__gte=start)
            else:
                return queryset.filter(time__lte=end)
        return queryset

    def filter_by_month_or_year(self, queryset):
        """
        Given optional month/year parameters, returns events in the specified
        month/year. Year defaults to current year.
        """
        month_str = self.request.query_params.get('month', None)
        month_int = self.parse_int(month_str)
        year_str = self.request.query_params.get('year', None)
        year_int = self.parse_int(year_str)
        curr_year_str = dateformat.format(timezone.now(), 'Y')
        curr_year_int = self.parse_int(curr_year_str)

        if month_str is not None and 1 <= month_int <= 12:
            if year_str is not None and 1999 <= year_int <= curr_year_int:
                return queryset.filter(time__year=year_str, time__month=month_str)
            elif curr_year_str is not None:
                return queryset.filter(time__year=curr_year_str, time__month=month_str)
        elif year_str is not None and 1999 <= year_int <= curr_year_int:
            return queryset.filter(time__year=year_str)
        return self.filter_by_date_range(queryset)

    def filter_by_time(self, queryset):
        """
        Given an optional time parameter, return events in the specified time
        period. Offers week and 7days option to facilitate frontend visualization.
        """
        today = timezone.now()
        date = today.date()
        month = dateformat.format(today, 'm')
        year = dateformat.format(today, 'Y')
        last_monday = today.date() - timedelta(days=today.weekday())
        this_monday = today.date() + timedelta(days=-today.weekday(), weeks=1)
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
            }.get(time, self.filter_by_month_or_year(queryset))
        return self.filter_by_month_or_year(queryset)

    def filter_by_link_or_user(self):
        """
        Given an optional link or username parameter, return events for the
        specified link(s). If not superuser, only returns events for user.
        """
        queryset = Event.objects.all()
        link_id = self.request.query_params.get('link', None)
        username = self.request.query_params.get('username', None)
        if link_id is not None:
            return queryset.filter(link=link_id)
        elif self.request.user.is_superuser and username is not None:
            return queryset.filter(link__creator__username=username)
        elif not self.request.user.is_superuser:
            return queryset.filter(link__creator=self.request.user)
        return queryset

    def get_queryset(self):
        """
        Given optional filtering parameters, return any corresponding events.
        """
        queryset = self.filter_by_link_or_user()
        queryset = self.filter_by_time(queryset)
        return queryset

    @action(detail=False, methods=['get'], url_path='stats', name='Event Stats')
    def get_event_stats(self, request):
        """
        Given a method parameter, returns event data in the specified format. Can
        return 'count' statistics or the original Event data.
        TODO: figure out return format according to recharts docs
        TODO: restrict date range for daily/weekly/monthly/yearly data
        TODO: stats by device type, geographic region, time of day/week
        """
        output = []
        queryset = self.filter_by_link_or_user()
        time = request.query_params.get('time', None)
        method = request.query_params.get('method', None)
        if time is not None:
            time = time.lower()

        if time not in ['daily', 'weekly', 'monthly', 'yearly']:
            if time is None:
                queryset = self.filter_by_month_or_year(queryset)
            else:
                queryset = self.filter_by_time(queryset)
            if method is not None and method.lower() == 'count':
                return Response({ 'count': queryset.count() })
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)

        queryset = {
            'daily': queryset.annotate(period=TruncDay('time')),
            'weekly': queryset.annotate(period=TruncWeek('time')),
            'monthly': queryset.annotate(period=TruncMonth('time')),
            'yearly': queryset.annotate(period=TruncYear('time')),
        }.get(time).order_by('period')

        # Fetches Event entry by primary key
        output = []
        queryset = queryset \
                    .values('period') \
                    .annotate(event_ids=ArrayAgg('id')) \
                    .values('period', 'event_ids')
        for q in queryset:
            data = list(EventSerializer(Event.objects.get(pk=id), many=False).data for id in q['event_ids'])
            output.append({ 
                'period': q['period'], 
                'count': len(data), 
                'events': data 
            })
        return Response(output)

    def create(self, request):
        """
        Creates an event for the specified link_id. Admins may specify a time
        parameter.
        """
        link_id = self.request.data.get('link', None)
        time = self.request.data.get('time', None)
        time = self.parse_date(time)

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
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)

    def list(self, request):
        """
        Returns user's preferences
        """
        username = self.request.query_params.get('username', None)
        if username is not None:
            if not user_exists(username):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset = Preference.objects.get(user__username=username)
        elif not request.user.is_anonymous:
            queryset = Preference.objects.get(user=request.user)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = (IsOwner,)

    def list(self, request):
        """
        Returns user's info
        """
        username = self.request.query_params.get('username', None)
        if username is not None:
            if not user_exists(username):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset = User.objects.get(username=username)
        elif not request.user.is_anonymous:
            queryset = User.objects.get(username=request.user)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(queryset)
        return Response(serializer.data)

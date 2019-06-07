from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.http import JsonResponse
from django.utils import timezone, dateformat
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from internal.models import Link, Event, Preference, IGToken
from internal.permissions import IsOwner, HasEventPermission
from internal.serializers import LinkSerializer, EventSerializer, PreferenceSerializer, UserSerializer
from datetime import datetime, timedelta
from dateutil import parser
from urllib.request import urlopen
import pdb
import requests
import pandas as pd
import json

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

class LinkViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows links to be viewed or edited.
    """
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
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

      serializer = self.serializer_class(queryset, many=True)
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
                return queryset.filter(date__range=[start, end])
            elif start:
                return queryset.filter(date__gte=start)
            else:
                return queryset.filter(date__lte=end)
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
                return queryset.filter(date__year=year_str, date__month=month_str)
            elif curr_year_str is not None:
                return queryset.filter(date__year=curr_year_str, date__month=month_str)
        elif year_str is not None and 1999 <= year_int <= curr_year_int:
            return queryset.filter(date__year=year_str)
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

        time = self.request.query_params.get('limit', None)
        if time is not None:
            time = time.lower()
            return {
                'latest': queryset.order_by('-date')[:1],
                'today': queryset.filter(date=date),
                'week': queryset.filter(date__range=[last_monday, this_monday]),
                'month': queryset.filter(date__year=year, date__month=month),
                '7days': queryset.filter(date__range=[last_7_days, today]),
                '30days': queryset.filter(date__range=[last_30_days, today]),
                '90days': queryset.filter(date__range=[last_90_days, today]),
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

    def generate_csv(self, queryset):
        data = EventSerializer(queryset, many=True).data
        df = pd.DataFrame(data)
        if not df.empty:
            df['url'] = df.link.apply(lambda row: row['url'])
            df['order'] = df.link.apply(lambda row: row['order'])
            df['text'] = df.link.apply(lambda row: row['text'])
            df.drop(columns=['link'], inplace=True)
        return (df.to_csv(index=False), json.loads(df.to_json(orient='values')))

    def get_daily_data(self, data):
        today = timezone.now()
        date = today.date()
        last_7_days = date - timedelta(days=7)
        last_30_days = date - timedelta(days=30)
        last_90_days = date - timedelta(days=90)

        time = self.request.query_params.get('limit', None)
        if time is not None:
            time = time.lower()

        start = self.request.query_params.get('start', None)
        start = self.parse_date(start)
        end = self.request.query_params.get('end', None)
        end = self.parse_date(end)

        start_date = date
        if data:
            start_date = list(data.keys())[0]
        end_date = date
        if time == '7days':
            start_date = last_7_days
        elif time == '30days':
            start_date = last_30_days
        elif time == '90days':
            start_date = last_90_days
        else:
            if start is not None:
                start_date = start
            if end is not None:
                end_date = end.replace(hour=23, minute=59, second=59)

        output = []
        daterange = pd.date_range(start_date, end_date)
        for single_date in daterange:
            output.append({
                'period': single_date,
                'count': data[single_date]['count'] if single_date in data else 0,
                'events': data[single_date]['events'] if single_date in data else [],
            })
        return output

    @action(detail=False, methods=['get'], url_path='stats', name='Event Stats')
    def get_event_stats(self, request):
        """
        Given a method parameter, returns event data in the specified format. Can
        return 'count' statistics or the original Event data.
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

        queryset = self.filter_by_time(queryset)

        # generate csv data
        (raw_data, raw_json) = self.generate_csv(queryset)

        queryset = {
            'daily': queryset.annotate(period=TruncDate('date')),
            'weekly': queryset.annotate(period=TruncWeek('date')),
            'monthly': queryset.annotate(period=TruncMonth('date')),
            'yearly': queryset.annotate(period=TruncYear('date')),
        }.get(time).order_by('period')

        # Fetches Event entry by primary key
        output = {}
        queryset = queryset \
                    .values('period') \
                    .annotate(event_ids=ArrayAgg('id')) \
                    .values('period', 'event_ids')
        for q in queryset:
            data = list(EventSerializer(Event.objects.get(pk=id), many=False).data for id in q['event_ids'])
            output[q['period']] = {
                'period': q['period'],
                'count': len(data),
                'events': data,
            }

        daily_data = self.get_daily_data(output)

        return Response({
            'data': daily_data,
            'raw_csv': raw_data,
            'raw': raw_json
        })

    def create(self, request):
        """
        Creates an event for the specified link_id. Admins may specify a time
        parameter.
        """
        link_id = self.request.data.get('link', None)
        # time = self.request.data.get('time', None)
        # time = self.parse_date(time)

        if link_id is not None:
            event = Event.objects.create(link_id=link_id)
            # if request.user.is_superuser and time is not None:
            #     event = Event.objects.create(link_id=link_id, time=time)
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

    @action(detail=False, methods=['post'], url_path='create_account', name='Create Account')
    def create_account(self, request):
        ig_token = request.data.get('token', None)
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        name = request.data.get('name', None).split(' ')
        first_name = name[0]
        if len(name) > 0:
            last_name = name[-1]
        else:
            last_name = ""
        image_url = request.data.get('profile_img', None)

        try:
            user = User.objects.get(username=username)
            return JsonResponse({'details': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            self.store_token(ig_token, user)
            self.download_and_store_image(user, image_url)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='igauth', name='IG Auth')
    def instagram_auth(self, request):
        code = request.query_params.get('code', None)
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = self.get_ig_response(code)
        if response.status_code is not status.HTTP_200_OK:
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        self.store_token(response, request.user)
        return Response(response.json(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='ig_response', name='IG Response')
    def get_ig_response_endpoint(self, request):
        code = request.query_params.get('code', None)
        response = self.get_ig_response(code)
        return Response(response.json(), status=response.status_code)

    def get_ig_response(self, code):
        data = {
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.REDIRECT_URI,
            'code': code,
        }
        URL = settings.IG_ACCESS_TOKEN_URL
        return requests.post(URL, data=data)

    def store_token(self, new_token, user):
        try:
            curr_token = IGToken.objects.get(user=user)
        except IGToken.DoesNotExist:
            curr_token = None
        if new_token is not None:
            if curr_token is None:
                curr_token = IGToken.objects.create(user=user)
            curr_token.ig_token = new_token
            curr_token.save()

    def download_and_store_image(self, user, image_url):
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urlopen(image_url).read())
        img_temp.flush()

        preference = Preference.objects.get(user=user)
        preference.profile_img.save('profile_pic.jpg', File(img_temp))
        preference.save()

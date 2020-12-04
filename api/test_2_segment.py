from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Segment
from .serializers import SegmentSerializer

SEGMENTS_URL = '/api/segments/'


def create_segment(segment_name):
    return Segment.objects.create(segment_name=segment_name)


def detail_url(segment_id):
    return reverse('api:segment-detail', args=[segment_id])


class AuthorizedSegmentApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_2_1_should_get_all_segments(self):
        create_segment(segment_name="SUV")
        create_segment(segment_name="Sedan")
        res = self.client.get(SEGMENTS_URL)
        segments = Segment.objects.all().order_by('id')
        serializer = SegmentSerializer(segments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_2_2_should_get_single_segment(self):
        segment = create_segment(segment_name="SUV")
        url = detail_url(segment.id)
        res = self.client.get(url)
        serializer = SegmentSerializer(segment)
        self.assertEqual(res.data, serializer.data)

    def test_2_3_should_create_new_segment_successfully(self):
        payload = {'segment_name': 'K-Car'}
        res = self.client.post(SEGMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Segment.objects.filter(
            segment_name=payload['segment_name']
        ).exists()
        self.assertTrue(exists)

    def test_2_4_should_not_create_new_segment_with_invalid(self):
        payload = {'segment_name': ''}
        res = self.client.post(SEGMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_2_5_should_partial_update_segment(self):
        segment = create_segment(segment_name="SUV")
        payload = {'segment_name': 'Compact SUV'}
        url = detail_url(segment.id)
        self.client.patch(url, payload)
        segment.refresh_from_db()
        self.assertEqual(segment.segment_name, payload['segment_name'])

    def test_2_6_should_update_segment(self):
        segment = create_segment(segment_name="SUV")
        payload = {'segment_name': 'Compact SUV'}
        url = detail_url(segment.id)
        self.client.put(url, payload)
        segment.refresh_from_db()
        self.assertEqual(segment.segment_name, payload['segment_name'])

    def test_2_7_should_delete_segment(self):
        segment = create_segment(segment_name="SUV")
        self.assertEqual(1, Segment.objects.count())
        url = detail_url(segment.id)
        self.client.delete(url)
        self.assertEqual(0, Segment.objects.count())


class UnauthorizedSegmentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_2_8_should_not_get_segments_when_unauthorized(self):
        res = self.client.get(SEGMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
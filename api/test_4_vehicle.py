from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Vehicle, Brand, Segment
from .serializers import VehicleSerializer
from decimal import Decimal

SEGMENTS_URL = '/api/segments/'
BRANDS_URL = '/api/brands/'
VEHICLES_URL = '/api/vehicles/'


def create_segment(segment_name):
    return Segment.objects.create(segment_name=segment_name)


def create_brand(brand_name):
    return Brand.objects.create(brand_name=brand_name)


def create_vehicle(user, **params):
    defaults = {
        'vehicle_name': 'MODEL S',
        'release_year': 2019,
        'price': 500.00,
    }
    defaults.update(params)

    return Vehicle.objects.create(user=user, **defaults)


def detail_seg_url(segment_id):
    return reverse('api:segment-detail', args=[segment_id])


def detail_brand_url(brand_id):
    return reverse('api:brand-detail', args=[brand_id])


def detail_vehicle_url(vehicle_id):
    return reverse('api:vehicle-detail', args=[vehicle_id])


class AuthorizedVehicleApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_4_1_should_get_vehicles(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        create_vehicle(user=self.user, segment=segment, brand=brand)
        create_vehicle(user=self.user, segment=segment, brand=brand)

        res = self.client.get(VEHICLES_URL)
        vehicles = Vehicle.objects.all().order_by('id')
        serializer = VehicleSerializer(vehicles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_4_2_should_get_single_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        url = detail_vehicle_url(vehicle.id)
        res = self.client.get(url)
        serializer = VehicleSerializer(vehicle)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_4_3_should_create_new_vehicle_successfully(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        payload = {
            'vehicle_name': 'MODEL S',
            'release_year': 2019,
            'price': 500.12,
            'segment': segment.id,
            'brand': brand.id,
        }
        res = self.client.post(VEHICLES_URL, payload)
        vehicle = Vehicle.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload['vehicle_name'], vehicle.vehicle_name)
        self.assertEqual(payload['release_year'], vehicle.release_year)
        self.assertAlmostEqual(Decimal(payload['price']),  vehicle.price, 2)
        self.assertEqual(payload['segment'], vehicle.segment.id)
        self.assertEqual(payload['brand'], vehicle.brand.id)

    def test_4_4_should_not_create_vehicle_with_invalid(self):
        payload = {
            'vehicle_name': 'MODEL S',
            'release_year': 2019,
            'price': 500.00,
            'segment': '',
            'brand': '',
        }
        res = self.client.post(VEHICLES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_4_5_should_partial_update_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        payload = {'vehicle_name': 'MODEL X'}
        url = detail_vehicle_url(vehicle.id)
        self.client.patch(url, payload)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.vehicle_name, payload['vehicle_name'])

    def test_4_6_should_update_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        payload = {
            'vehicle_name': 'MODEL X',
            'release_year': 2019,
            'price': 600.00,
            'segment': segment.id,
            'brand': brand.id,
        }
        url = detail_vehicle_url(vehicle.id)
        self.assertEqual(vehicle.vehicle_name, 'MODEL S')
        self.client.put(url, payload)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.vehicle_name, payload['vehicle_name'])

    def test_4_7_should_delete_vehicle(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        vehicle = create_vehicle(user=self.user, segment=segment, brand=brand)
        self.assertEqual(1, Vehicle.objects.count())
        url = detail_vehicle_url(vehicle.id)
        self.client.delete(url)
        self.assertEqual(0, Vehicle.objects.count())

    def test_4_8_should_cascade_delete_vehicle_by_segment_delete(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        create_vehicle(user=self.user, segment=segment, brand=brand)
        self.assertEqual(1, Vehicle.objects.count())
        url = detail_seg_url(segment.id)
        self.client.delete(url)
        self.assertEqual(0, Vehicle.objects.count())

    def test_4_9_should_cascade_delete_vehicle_by_brand_delete(self):
        segment = create_segment(segment_name='Sedan')
        brand = create_brand(brand_name='Tesla')
        create_vehicle(user=self.user, segment=segment, brand=brand)
        self.assertEqual(1, Vehicle.objects.count())
        url = detail_brand_url(brand.id)
        self.client.delete(url)
        self.assertEqual(0, Vehicle.objects.count())


class UnauthorizedVehicleApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_4__10_should_not_get_vehicles_when_unauthorized(self):
        res = self.client.get(VEHICLES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)






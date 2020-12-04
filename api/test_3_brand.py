from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Brand
from .serializers import BrandSerializer

BRANDS_URL = '/api/brands/'


def create_brand(brand_name):
    return Brand.objects.create(brand_name=brand_name)


def detail_url(brand_id):
    return reverse('api:brand-detail', args=[brand_id])


class AuthorizedBrandApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dummy', password='dummy_pw')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_3_1_should_get_brands(self):
        create_brand(brand_name="Toyota")
        create_brand(brand_name="Tesla")
        res = self.client.get(BRANDS_URL)
        brands = Brand.objects.all().order_by('id')
        serializer = BrandSerializer(brands, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_3_2_should_get_single_brand(self):
        brand = create_brand(brand_name="Toyota")
        url = detail_url(brand.id)
        res = self.client.get(url)
        serializer = BrandSerializer(brand)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_3_3_should_create_new_brand_successfully(self):
        payload = {'brand_name': 'Audi'}
        res = self.client.post(BRANDS_URL, payload)
        exists = Brand.objects.filter(
            brand_name=payload['brand_name']
        ).exists()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_3_4_should_not_create_brand_with_invalid(self):
        payload = {'brand_name': ''}
        res = self.client.post(BRANDS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_3_5_should_partial_update_brand(self):
        brand = create_brand(brand_name="Toyota")
        payload = {'brand_name': 'Lexus'}
        url = detail_url(brand.id)
        self.client.patch(url, payload)
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, payload['brand_name'])

    def test_3_6_should_update_brand(self):
        brand = create_brand(brand_name="Toyota")
        payload = {'brand_name': 'Lexus'}
        url = detail_url(brand.id)
        self.client.put(url, payload)
        brand.refresh_from_db()
        self.assertEqual(brand.brand_name, payload['brand_name'])

    def test_3_7_should_delete_brand(self):
        brand = create_brand(brand_name="Toyota")
        self.assertEqual(1, Brand.objects.count())
        url = detail_url(brand.id)
        self.client.delete(url)
        self.assertEqual(0, Brand.objects.count())


class UnauthorizedBrandApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_3_8_should_not_get_brands_when_unauthorized(self):
        res = self.client.get(BRANDS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)




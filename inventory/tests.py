"""
Tests for the inventory app
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Item


class ItemModelTest(TestCase):
    """Test cases for Item model"""
    
    def setUp(self):
        """Set up test data"""
        self.item_data = {
            'name': 'Test Item',
            'description': 'A test item',
            'quantity': 10,
            'price': 29.99,
            'category': 'Electronics'
        }
    
    def test_item_creation(self):
        """Test item creation"""
        item = Item(**self.item_data)
        item.save()
        
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.price, 29.99)
        self.assertEqual(item.category, 'Electronics')
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)
    
    def test_item_to_dict(self):
        """Test item to_dict method"""
        item = Item(**self.item_data)
        item.save()
        
        item_dict = item.to_dict()
        self.assertIn('id', item_dict)
        self.assertEqual(item_dict['name'], 'Test Item')
        self.assertEqual(item_dict['quantity'], 10)
    
    def test_item_str_representation(self):
        """Test item string representation"""
        item = Item(**self.item_data)
        self.assertEqual(str(item), 'Test Item - Electronics')


class ItemAPITest(APITestCase):
    """Test cases for Item API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.item_data = {
            'name': 'Test API Item',
            'description': 'A test item for API',
            'quantity': 5,
            'price': 15.50,
            'category': 'Books'
        }
        
        # Create a test item
        self.item = Item(**self.item_data)
        self.item.save()
    
    def test_get_items_list(self):
        """Test GET /api/items/"""
        url = reverse('item_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    @patch('inventory.views.send_websocket_message')
    def test_create_item(self, mock_websocket):
        """Test POST /api/items/"""
        url = reverse('item_list')
        new_item_data = {
            'name': 'New Item',
            'description': 'A new test item',
            'quantity': 3,
            'price': 25.00,
            'category': 'Tools'
        }
        
        response = self.client.post(url, new_item_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Item')
        mock_websocket.assert_called_once()
    
    def test_get_item_detail(self):
        """Test GET /api/items/{id}/"""
        url = reverse('item_detail', kwargs={'item_id': str(self.item.id)})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test API Item')
    
    @patch('inventory.views.send_websocket_message')
    def test_update_item(self, mock_websocket):
        """Test PUT /api/items/{id}/"""
        url = reverse('item_detail', kwargs={'item_id': str(self.item.id)})
        updated_data = {
            'name': 'Updated Item',
            'description': 'Updated description',
            'quantity': 15,
            'price': 30.00,
            'category': 'Books'
        }
        
        response = self.client.put(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Item')
        mock_websocket.assert_called_once()
    
    @patch('inventory.views.send_websocket_message')
    def test_delete_item(self, mock_websocket):
        """Test DELETE /api/items/{id}/"""
        url = reverse('item_detail', kwargs={'item_id': str(self.item.id)})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deleted', response.data['message'])
        mock_websocket.assert_called_once()
        
        # Verify item is deleted
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_nonexistent_item(self):
        """Test GET /api/items/{nonexistent_id}/"""
        url = reverse('item_detail', kwargs={'item_id': '507f1f77bcf86cd799439011'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_item_invalid_data(self):
        """Test POST /api/items/ with invalid data"""
        url = reverse('item_list')
        invalid_data = {
            'name': '',  # Required field empty
            'price': -10,  # Negative price
        }
        
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_health_check(self):
        """Test health check endpoint"""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')


class CacheTest(APITestCase):
    """Test cases for caching functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.item_data = {
            'name': 'Cache Test Item',
            'description': 'Item for cache testing',
            'quantity': 1,
            'price': 10.00,
            'category': 'Test'
        }
        
        self.item = Item(**self.item_data)
        self.item.save()
    
    @patch('inventory.views.cache')
    def test_cache_on_get_items(self, mock_cache):
        """Test that items are cached on GET request"""
        mock_cache.get.return_value = None
        mock_cache.set = MagicMock()
        
        url = reverse('item_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cache.set.assert_called_once()
    
    @patch('inventory.views.cache')
    def test_cache_invalidation_on_create(self, mock_cache):
        """Test that cache is invalidated on item creation"""
        mock_cache.delete = MagicMock()
        
        url = reverse('item_list')
        new_item_data = {
            'name': 'New Cache Item',
            'quantity': 1,
            'price': 5.00,
            'category': 'Test'
        }
        
        with patch('inventory.views.send_websocket_message'):
            response = self.client.post(url, new_item_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_cache.delete.assert_called()

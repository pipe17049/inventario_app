"""
Views for the inventory app
"""
import logging
import threading
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer

logger = logging.getLogger(__name__)

# Global WebSocket server reference (will be set when websocket_server is imported)
websocket_server_instance = None


def set_websocket_server(server_instance):
    """Set the WebSocket server instance"""
    global websocket_server_instance
    websocket_server_instance = server_instance


def get_cache_key(item_id=None):
    """Generate cache key for items"""
    if item_id:
        return f"item_{item_id}"
    return "all_items"


def invalidate_cache():
    """Invalidate all item-related cache"""
    cache.delete("all_items")


def send_websocket_message(message_type, data):
    """Send message to WebSocket server via direct function call"""
    try:
        # Import here to avoid circular imports
        from websocket_server import send_websocket_notification
        send_websocket_notification(message_type, data)
        logger.info(f"WebSocket message sent: {message_type}")
    except Exception as e:
        logger.error(f"Error sending WebSocket message: {e}")


@api_view(['GET', 'POST'])
def item_list(request):
    """
    List all items or create a new item
    """
    if request.method == 'GET':
        # Try to get from cache first
        cache_key = get_cache_key()
        cached_items = cache.get(cache_key)
        
        if cached_items is not None:
            logger.info("Items retrieved from cache")
            return Response(cached_items)
        
        # If not in cache, get from database
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        
        # Cache the result
        cache.set(cache_key, serializer.data, settings.CACHE_TTL)
        logger.info("Items retrieved from database and cached")
        
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            
            # Invalidate cache
            invalidate_cache()
            
            # Send WebSocket notification
            send_websocket_message('item_created', serializer.data)
            
            logger.info(f"Item created: {item.name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def item_detail(request, item_id):
    """
    Retrieve, update or delete an item
    """
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return Response(
            {'error': 'Item not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        # Try to get from cache first
        cache_key = get_cache_key(item_id)
        cached_item = cache.get(cache_key)
        
        if cached_item is not None:
            logger.info(f"Item {item_id} retrieved from cache")
            return Response(cached_item)
        
        serializer = ItemSerializer(item)
        
        # Cache the result
        cache.set(cache_key, serializer.data, settings.CACHE_TTL)
        logger.info(f"Item {item_id} retrieved from database and cached")
        
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            updated_item = serializer.save()
            
            # Invalidate cache
            invalidate_cache()
            cache.delete(get_cache_key(item_id))
            
            # Send WebSocket notification
            send_websocket_message('item_updated', serializer.data)
            
            logger.info(f"Item updated: {updated_item.name}")
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item_name = item.name
        
        item.delete()
        
        # Invalidate cache
        invalidate_cache()
        cache.delete(get_cache_key(item_id))
        
        # Send WebSocket notification for deletion
        send_websocket_message('item_deleted', {
            'id': item_id,
            'name': item_name,
            'message': f'Item "{item_name}" has been deleted'
        })
        
        logger.info(f"Item deleted: {item_name}")
        return Response(
            {'message': f'Item "{item_name}" has been deleted'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint with database connectivity test
    """
    try:
        # Test database connection by querying items count
        from .models import Item
        Item.objects.count()  # Forces a database query
        
        return Response({
            'status': 'healthy',
            'message': 'Inventory API is running',
            'database': 'connected'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}',
            'database': 'disconnected'
        }, status=503)

"""
MongoDB models using MongoEngine
"""
from mongoengine import Document, StringField, IntField, FloatField, DateTimeField
from datetime import datetime


class Item(Document):
    """
    Item model for inventory management
    """
    name = StringField(max_length=200, required=True)
    description = StringField(max_length=1000, required=False)
    quantity = IntField(min_value=0, default=0)
    price = FloatField(min_value=0.0, required=True)
    category = StringField(max_length=100, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'items',
        'indexes': [
            'name',
            'category',
            'created_at'
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.category}"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

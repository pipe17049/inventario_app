"""
Factory classes for creating test data
"""
import factory
from datetime import datetime
from .models import Item


class ItemFactory(factory.Factory):
    """Factory for creating Item instances"""
    
    class Meta:
        model = Item
    
    name = factory.Sequence(lambda n: f"Test Item {n}")
    description = factory.Faker('text', max_nb_chars=200)
    quantity = factory.Faker('random_int', min=0, max=100)
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    category = factory.Faker('random_element', 
                           elements=('Electronics', 'Books', 'Clothing', 'Tools', 'Food', 'Other'))
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)

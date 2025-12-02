# Test package for order app

# Import all tests from the order_tests module (tests.py in parent directory)
# and from test files within this package
from .test_base import *

# Import from tests.py at the parent level
import sys
import importlib.util

# Load tests.py as a module
_tests_file_path = __file__.replace('__init__.py', '../tests.py').replace('tests/../', '')
_spec = importlib.util.spec_from_file_location("order_tests", _tests_file_path)
_order_tests = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_order_tests)

# Export test classes from tests.py
ShippingAddressModelTestCase = _order_tests.ShippingAddressModelTestCase
OrderModelTestCase = _order_tests.OrderModelTestCase
OrderItemModelTestCase = _order_tests.OrderItemModelTestCase
PaymentModelTestCase = _order_tests.PaymentModelTestCase
ProductRatingModelTestCase = _order_tests.ProductRatingModelTestCase
OrderViewsTestCase = _order_tests.OrderViewsTestCase
CheckoutResultTestCase = _order_tests.CheckoutResultTestCase
ProcessCheckoutServiceTestCase = _order_tests.ProcessCheckoutServiceTestCase

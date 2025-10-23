import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becathlon.settings')
django.setup()

from django.contrib.auth.models import User
from apps.profiles.models import Profile

# Create or get the test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)

if created:
    user.set_password('testpass123')
    user.save()
    print(f'User "testuser" created successfully')
else:
    print(f'User "testuser" already exists')
    # Update password anyway
    user.set_password('testpass123')
    user.save()
    print('Password updated')

# Make sure profile exists
if not hasattr(user, 'profile'):
    Profile.objects.get_or_create(user=user)
    print('Profile created')
else:
    print('Profile already exists')

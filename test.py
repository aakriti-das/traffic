import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffisight.settings')  # Replace 'traffic' with your actual project name
django.setup()

from user_app.views import get_mac_address

text=get_mac_address()
print(text)
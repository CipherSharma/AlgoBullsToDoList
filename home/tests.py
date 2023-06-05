from django.test import TestCase
from datetime import datetime
# Create your tests here.
date=datetime.strptime("22-09-2022", "%d-%m-%Y")
if date<datetime.now():
    print("false")

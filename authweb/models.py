from django.db import models
from django.utils import timezone
from datetime import timedelta
import hashlib


class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Assume OTP expires after 5 minutes
        expiration_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiration_time

    @staticmethod
    def hash_otp(otp):
        # A simple hashing function for the OTP
        return hashlib.sha256(otp.encode()).hexdigest()

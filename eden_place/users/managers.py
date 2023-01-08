
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, user_id, email=None, username=None, is_staff=False, is_student=True, password=None):
        if not password:
            raise ValueError("User must have a Password!")

        if not user_id:
            raise ValueError("User must have an id!")
        
        user = self.model(
            user_id=user_id,
        )
        user.username = username
        if email:
            user.email = self.normalize_email(email=email)
        if is_staff is True:
            user.is_staff = True
        if is_student is True:
            user.is_student = True
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, email, username, password):
        user = self.create_user(
            user_id=user_id,
            password=password,
            is_student=False,
            username=username,
            email=email,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    




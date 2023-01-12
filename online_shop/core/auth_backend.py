from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import CustomUser

class CustomModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(CustomUser.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            users = CustomUser._default_manager.filter(Q(email__exact=username) | Q(username__exact=username))
        except CustomUser.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            CustomUser().set_password(password)
        else:
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            else:
                CustomUser().set_password(password)
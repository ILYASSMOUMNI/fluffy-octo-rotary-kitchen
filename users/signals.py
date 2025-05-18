from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.conf import settings
from .models import UserSession, User

@receiver(user_logged_in)
def enforce_single_session(sender, user, request, **kwargs):
    # Get the current session key
    current_session_key = request.session.session_key
    if not current_session_key:
        request.session.create()
        current_session_key = request.session.session_key

    # Try to get the user's previous session
    try:
        user_session = UserSession.objects.get(user=user)
        old_session_key = user_session.session_key
        if old_session_key and old_session_key != current_session_key:
            # Delete the old session from the session store
            Session.objects.filter(session_key=old_session_key).delete()
        user_session.session_key = current_session_key
        user_session.save()
    except UserSession.DoesNotExist:
        UserSession.objects.create(user=user, session_key=current_session_key) 
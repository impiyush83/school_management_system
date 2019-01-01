from school_management_app.models import User


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except:
        return None

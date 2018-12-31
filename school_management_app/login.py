from school_management_app.models import User


def check_authenticated(username, password):
    user = User.objects.get(username=username, password=password)
    return user

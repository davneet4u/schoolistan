from functools import wraps
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.conf import settings


# decorators for web users ----------------------------
def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 1:
                return function(request, *args, **kwargs)
            else:
                messages.error(request, 'Your account is not an admin account. Please login with admin account')
                return HttpResponseRedirect(settings.ADMIN_LOGIN_URL)                
        else:
            messages.error(request, 'Login is required to access dashboard.')
            return HttpResponseRedirect(settings.ADMIN_LOGIN_URL)
    return wrap


def staff_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role in (1, 2):
                return function(request, *args, **kwargs)
            else:
                messages.error(request, 'Your account is not an staff account. Please login with staff account')
                return HttpResponseRedirect(settings.ADMIN_LOGIN_URL)
        else:
            messages.error(request, 'Login is required to access dashboard.')
            return HttpResponseRedirect(settings.ADMIN_LOGIN_URL)
    return wrap


def teacher_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role in (1, 2, 3):
                return function(request, *args, **kwargs)
            else:
                messages.error(request, 'Your account is not an moderator account. Please login with moderator account.')
                return HttpResponseRedirect(settings.ADMIN_LOGIN_URL)
        else:
            messages.error(request, 'Login is required to access dashboard.')
            return HttpResponseRedirect(settings.ADMIN_LOGIN_URL)
    return wrap

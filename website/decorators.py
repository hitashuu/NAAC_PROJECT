from django.shortcuts import redirect
from functools import wraps

def login_or_head_required(view_func):
    @wraps(view_func)
    def wrapper(request):
        if request.user.is_authenticated or request.session.get("is_head") or request.session.get("is_admin"):

            return view_func(request)
        else:
            return redirect('login_view')  
    return wrapper

def admin_or_head_required(view_func):
    @wraps(view_func)
    def wrapper(request):
        if request.session.get("is_head") or request.session.get("is_admin"):

            return view_func(request)
        else:
            return redirect('login_view')  
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request):
        if request.session.get("is_admin"):

            return view_func(request)
        else:
            return redirect('login_view')  
    return wrapper


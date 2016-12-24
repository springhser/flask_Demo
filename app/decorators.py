# -*- coding: utf-8 -*-
"""
Created on 16-11-22 /下午5:43
@author: Chen Jinbin
检查用户权限的自定义修饰器
"""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    # return permission_required(current_app.config[''])(f)
    # 此处current_app 上下文没有被激活
    return permission_required(Permission.ADMIN)(f)

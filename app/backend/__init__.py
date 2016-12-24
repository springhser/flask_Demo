# -*- coding: utf-8 -*-
"""
Created on 16-12-9 /下午10:16
@author: Chen Jinbin
"""
from flask import Blueprint

backend = Blueprint('backend', __name__)

from . import views

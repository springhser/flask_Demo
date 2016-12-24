# -*- coding: utf-8 -*-
"""
Created on 16-11-22 /上午10:04
@author: Chen Jinbin
"""
from flask import render_template, request, jsonify
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(505)
def internal_server_error(e):
    return render_template('errors/505.html'), 505

@main.app_errorhandler(403)
def  forbidden(e):
    return render_template('errors/403.html'), 403

#
# @main.app_errorhandler(403)
# def forbidden(e):
#     if request.accept_mimetypes.accept_json and \
#             not request.accept_mimetypes.accept_html:
#         response = jsonify({'error': 'forbidden'})
#         response.status_code = 403
#         return response
#     return render_template('403.html'), 403


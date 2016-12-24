# -*- coding: utf-8 -*-
"""
Created on 16-11-21 /上午9:12
@author: Chen Jinbin
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from config import config
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField

bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()
pagedown = PageDown()

pic = UploadSet('pic')

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)  # 这个不懂

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    configure_uploads(app, pic)
    #登录管理器
    login_manager.init_app(app)

    #注册蓝本
    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .backend import backend as backend_blueprint
    app.register_blueprint(backend_blueprint, url_prefix='/backend')

    return app







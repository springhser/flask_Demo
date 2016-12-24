# -*- coding: utf-8 -*-
"""
Created on 16-11-22 /下午2:02
@author: Chen Jinbin
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from ..models import User

#登录表单
class LoginForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'进去')

#注册表单
class RegisterForm(FlaskForm):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'大名', validators=[Required(), Length(1, 32),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          u'用户名必须以字母开头，可以是字母，数字，'
                                                          u'点号和下划线的组合')])
    password = PasswordField(u'暗号', validators=[Required(),
                                                     EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField(u'再喊一遍', validators=[Required()])
    submit = SubmitField(u'加入')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

# 修改密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u"现密码", validators=[DataRequired()])
    new_password = PasswordField(u"新密码", validators=[DataRequired()])
    new_password2 = PasswordField(u"再次输入", validators=[DataRequired(),
                                                       EqualTo('new_password', message=u"新密码必须相同匹配")])
    submit = SubmitField(u"提交")

# 重置密码请求表单（填入邮箱地址，发送重置邮件）
class PasswordResetReqForm(FlaskForm):
    email = StringField(u"邮箱地址", validators=[DataRequired(), Email(), Length(4,64)])
    submit = SubmitField(u"发送邮件")
# 重置密码表单
class ResetPasswordForm(FlaskForm):
    email = StringField(u"邮箱", validators=[DataRequired(), Email(), Length(4,64)])
    new_password = PasswordField(u"新密码", validators=[DataRequired()])
    new_password2 = PasswordField(u"再次输入", validators=[DataRequired(),
                                                       EqualTo('new_password', message=u"新密码必须相同匹配")])
    submit = SubmitField(u"提交")

    def verify_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("Email is none")

class ResetEmailForm(FlaskForm):
    email = StringField(u"新邮箱", validators=[DataRequired(), Email(), Length(4, 64)])
    submit = SubmitField(u"提交")
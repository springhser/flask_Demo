# -*- coding: utf-8 -*-
"""
Created on 16-11-22 /下午4:03
@author: Chen Jinbin
"""
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField,\
                    SelectField
from wtforms.validators import Length, Email, Regexp, EqualTo, DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from .. import pic
from wtforms import ValidationError

# 编辑个人信息表单
class EditProfileForm(FlaskForm):
    img = FileField(u"上传头像", validators=[
                       FileRequired(), FileAllowed(pic, u'只能上传Images!')])
    username= StringField(u"修改用户名",validators=[Length(1, 32),
                                                   Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                          u'用户名必须以字母开头,可以是字母,数字,'
                                                          u'点号和下划线的组合')])
    submit = SubmitField(u"提交")

# 编辑博客评论表单
class EditCommentForm(FlaskForm):
    body = PageDownField(u"内容", validators=[DataRequired()])
    submit = SubmitField(u"提交")

# 练习表单
class SelectForm(FlaskForm):
    test = SelectField(u"sss", choices=[('0', u'全部'),('1', u'待审核'),('2', u'认证成功'),
                                        ('3', u'认证失败')] )
    submit = SubmitField(u"a")
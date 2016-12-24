# -*- coding: utf-8 -*-
"""
Created on 16-12-9 /下午10:17
@author: Chen Jinbin
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, SelectField,FileField
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length
from ..models import Classification
from .. import pic

"""
choices 列表在表单的构造函数中设定，其值从 Department 模型中获取，使用一个查询按照类型id顺序排列所有类型
，元组中的标识符是类型的 id，因为这是个整数，所以在 SelectField 构造函数中添加 coerce=int 参数，从而把字
段的值转换为整数
"""
# 博客编辑表单
class EditPostForm(FlaskForm):
    title = StringField(u"标题", validators=[DataRequired()])
    classification = SelectField(u"分类标签", coerce=int)
    body = PageDownField(u"内容", validators=[DataRequired()])
    submit = SubmitField(u"提交")

    def __init__(self, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.classification.choices = [(classification.id, classification.name)
                                       for classification in Classification.query.order_by(Classification.id).all()]

        # self.user = user

# 增加分类表单
class AddClassificationForm(FlaskForm):
    name = StringField(u"分类名称", validators=[DataRequired(), Length(1, 64)])
    img = FileField(u"分类图片", validators=[
        FileRequired(), FileAllowed(pic, u'只能上传Images!')])
    brief = StringField(u"简介",validators=[DataRequired()])
    submit = SubmitField(u"提交")

    # def validate_name(self, field):
    #     # if User.query.filter_by(email=field.data).first():
    #     #     raise ValidationError('email already registered.')
    #     if Classification.query.filter_by(name=field.data).first():
    #         raise ValidationError('class already exist')

# 编辑公告表单
class EditMessageForm(FlaskForm):
    content = PageDownField(u"内容", validators=[DataRequired()])
    submit = SubmitField(u"提交")

# 上传网站图片
class UpdateImageForm(FlaskForm):
    img = FileField(u"上传头像", validators=[
                       FileRequired(), FileAllowed(pic, u'只能上传Images!')])
    submit = SubmitField(u"提交")

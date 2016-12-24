# -*- coding: utf-8 -*-
"""
Created on 16-12-9 /下午10:16
@author: Chen Jinbin
"""
import os, shutil
from . import backend
from ..decorators import admin_required
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request, current_app
from forms import AddClassificationForm, EditPostForm, EditMessageForm, UpdateImageForm
from .. import db, pic
from ..models import Classification, Post, User, Comment, Permission, Message
from datetime import datetime

# @backend.route('/adm')
# @login_required
# @admin_required
# def forbid():
#     return render_template('backend/backend.html')


# 后台首页
@backend.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    return render_template('backend/backend.html')


# 增加分类
@backend.route('/add_class', methods=['GET', 'POST'])
# @login_required
# @admin_required
def add_class():
    form = AddClassificationForm()
    if form.validate_on_submit():
        if form.img.data:
            img_path = current_app.config['UPLOADED_PIC_DEST']+"/classes"+\
                       "/"+form.name.data
            # flash(img_path)
            if os.path.exists(img_path):
                shutil.rmtree(img_path)
                flash(u"删除成功")
            else:
                flash(img_path)
            strlist = str(form.img.data.filename).split(".")
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "." + strlist[-1]
            # filename = form.username.data + "." + strlist[len(strlist) - 1]
            url = pic.save(form.img.data, folder="classes"+"/"+form.name.data
                           , name=filename)
            flash(url)
            img_src = 'pic/'+"classes"+"/"+form.name.data+"/"+filename
        classification = Classification(name=form.name.data,
                                        img_src=img_src,
                                        brief=form.brief.data)
        db.session.add(classification)
        # db.session.commit()
        flash(u"增加分类成功")
        return redirect(url_for("backend.add_class"))
    classes = Classification.query.order_by(Classification.id.asc()).all()
    return render_template('backend/add_class.html', form=form, classes=classes)

# 修改分类
@backend.route('/update_class/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def update_class(id):
    form = AddClassificationForm()
    cur_class = Classification.query.get_or_404(id)
    if form.validate_on_submit():
        if form.img.data:
            img_path = current_app.config['UPLOADED_PIC_DEST']+"/classes"+\
                       "/"+form.name.data
            # flash(img_path)
            if os.path.exists(img_path):
                shutil.rmtree(img_path)
                flash(u"删除成功")
            else:
                flash(img_path)
            strlist = str(form.img.data.filename).split(".")
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "." + strlist[-1]
            # filename = form.username.data + "." + strlist[len(strlist) - 1]
            url = pic.save(form.img.data, folder="classes"+"/"+form.name.data
                           , name=filename)
            flash(url)
            img_src = 'pic/'+"classes"+"/"+form.name.data+"/"+filename
        cur_class.name = form.name.data
        cur_class.img_src = img_src
        cur_class.brief = form.brief.data
        db.session.add(cur_class)
        # db.session.commit()
        flash(u"修改分类成功")
        return redirect(url_for("backend.add_class"))
    form.name.data = cur_class.name
    form.brief.data = cur_class.brief
    classes = Classification.query.order_by(Classification.id.asc()).all()
    return render_template('backend/add_class.html', form=form, classes=classes)

# 删除类型
@backend.route('/remove_class/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def remove_class(id):
    cur_class = Classification.query.get_or_404(id)
    db.session.remove(cur_class)
    flash(u"删除成功")
    return redirect(url_for("backend.add_class"))

# 编辑博客
@backend.route('/edit_post', methods=['GET', 'POST'])
# @login_required
# @admin_required
def edit_post():
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    class_id=form.classification.data)
        db.session.add(post)
        db.session.commit()
        flash(u"编辑博客成功")
        return redirect(url_for("main.show_post", post_id=post.id))
    classes = Classification.query.all()
    return render_template('backend/edit_post.html', form=form, classes=classes)


# 后台的用户列表
@backend.route('/user_list', methods=['GET', 'POST'])
# @login_required
# @admin_required
def show_user_list():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.member_since.asc()).paginate(
        page, per_page=5, error_out=False)
    users = pagination.items
    return render_template('backend/_user_list.html', users=users,
                           pagination=pagination, Permission=Permission)

# 禁止用户评论
@backend.route('/forbid/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def forbid_comment(id):
    user = User.query.filter_by(id=id).first()
    if user is not None:
        user.permissions = 3  # 权限为3的用户没有评论权
        db.session.add(user)
        db.session.commit()
        flash(u"您刚刚让"+user.username+u"闭嘴了")
    else:
        flash(u"操作没有成功哦")
    return redirect(url_for("backend.show_user_list"))

# 删除用户，不到不得已不这样做
@backend.route('/remove_user/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def remove_user(id):
    user = User.query.filter_by(id=id).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(u"您刚刚让"+user.username+u"消失了")
    else:
        flash(u"操作没有成功哦")
    return redirect(url_for("backend.show_user_list"))

# 显示博列表
@backend.route('/show_post_list', methods=['GET', 'POST'])
# @login_required
# @admin_required
def show_post_list():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.asc()).paginate(
        page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('backend/_post_list.html', posts=posts,
                           pagination=pagination)

# 修改博客
@backend.route('/update_post/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def update_post(id):
    form=EditPostForm()
    post = Post.query.get_or_404(id)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.class_id = form.classification.data
        post.last_update = datetime.utcnow()
        db.session.add(post)
        db.session.commit()
        flash(u"编辑博客成功")
        return redirect(url_for("main.show_post", post_id=post.id))
    classes = Classification.query.all()
    form.title.data = post.title
    form.body.data = post.body
    form.classification.data = post.class_id
    return render_template('backend/edit_post.html', form=form, classes=classes)

# 删除博客
@backend.route('/remove_post/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def remove_post(id):
    post = Post.query.filter_by(id=id).first()
    if post is not None:
        db.session.delete(post)
        db.session.commit()
        flash(u"您刚刚删除了一篇文章文章")
    else:
        flash(u"操作没有成功哦")
    return redirect(url_for("backend.show_post_list"))

# 管理用户评论
@backend.route('/manage_comment', methods=['GET', 'POST'])
# @login_required
# @admin_required
def manage_comment():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('backend/_comment_list.html', comments=comments,
                           pagination=pagination)

# 关闭评论
@backend.route('/close_comment/<int:id>')
# @login_required
# @admin_required
def close_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('backend.manage_comment',
                            page=request.args.get('page', 1, type=int)))

# 显示评论
@backend.route('/enable_comment/<int:id>')
# @login_required
# @admin_required
def enable_comment(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('backend.manage_comment',
                            page=request.args.get('page', 1, type=int)))

# 网站消息管理
@backend.route('/manage_message', methods=['GET', 'POST'])
# @login_required
# @admin_required
def manage_message():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(
        page, per_page=5, error_out=False)
    messages = pagination.items
    return render_template('/backend/_message_list.html',
                           pagination=pagination, messages=messages)

# 编辑公告
@backend.route('/edit_message', methods=['GET', 'POST'])
# @login_required
# @admin_required
def edit_message():
    form = EditMessageForm()
    if form.validate_on_submit():
        message = Message(content=form.content.data,
                          last_update=datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('backend.manage_message'))
    return render_template('/backend/edit_message.html', form=form)

# 修改公告
@backend.route('/update_message/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def update_message(id):
    form = EditMessageForm()
    message = Message.query.get_or_404(id)
    if form.validate_on_submit():
        message.content = form.content.data
        message.last_update =datetime.utcnow()
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('backend.manage_message'))
    form.content.data = message.content
    return render_template('/backend/edit_message.html', form=form)

# 显示公告
@backend.route('/release_message/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def release_message(id):
    message = Message.query.get_or_404(id)
    message.enable = True
    db.session.add(message)
    db.session.commit()
    flash(u'公告已显示')
    return redirect(url_for('backend.manage_message'))

# 关闭公告
@backend.route('/cancel_message/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def cancel_message(id):
    message = Message.query.get_or_404(id)
    message.enable = False
    db.session.add(message)
    db.session.commit()
    flash(u'公告已关闭')
    return redirect(url_for('backend.manage_message'))

# 图片及管理员个人信息管理
@backend.route('/manage_img', methods=['GET', 'POST'])
# @login_required
# @admin_required
def manage_img():
    if os.path.exists("./app/static/pic/background"):
        filename1 = os.listdir("./app/static/pic/background")[0]
    else:
        filename1 = None
    if os.path.exists("./app/static/pic/moren"):
        filename2 = os.listdir("./app/static/pic/moren")[0]
    else:
        filename2 = None
    return render_template("backend/_edit_img.html", filename1=filename1,
                           filename2=filename2)

@backend.route('/change_img/<type>', methods=['GET', 'POST'])
# @login_required
# @admin_required
def change_img(type):
    form = UpdateImageForm()
    filename = None
    if type == "background":
        if form.validate_on_submit():
            if form.img.data:
                img_path = current_app.config['UPLOADED_PIC_DEST']+"/"+type
                if os.path.exists(img_path):
                    shutil.rmtree(img_path)
                    flash(u"删除成功")
                else:
                    flash(img_path)
                strlist = str(form.img.data.filename).split(".")
                filename = type + "." + strlist[-1]
                url = pic.save(form.img.data, folder=type
                               , name=filename)
                flash(url)
            return redirect(url_for('backend.manage_img'))
    if type == "moren":
        if form.validate_on_submit():
            if form.img.data:
                img_path = current_app.config['UPLOADED_PIC_DEST']+"/"+type
                if os.path.exists(img_path):
                    shutil.rmtree(img_path)
                    flash(u"删除成功")
                else:
                    flash(img_path)
                strlist = str(form.img.data.filename).split(".")
                filename = type + "." + strlist[-1]
                url = pic.save(form.img.data, folder=type
                               , name=filename)
                flash(url)
            return redirect(url_for('backend.manage_img'))
    return render_template("backend/change_img.html", form=form)

# 日志管理











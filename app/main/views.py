# -*- coding: utf-8 -*-
"""
Created on 16-11-22 /下午4:03
@author: Chen Jinbin
"""
import os, shutil
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from flask_login import login_required, current_user
from ..decorators import admin_required
from .. import db, pic
from ..models import User, Post, Classification, Comment, Permission, Message
from flask import abort, request, current_app
from forms import EditProfileForm, SelectForm, EditCommentForm
from .import main  # 蓝本构建的必要导入
# from flask_uploads import UploadSet, IMAGES, configure_uploads


@main.route('/', methods=['GET', 'POST'])
def index():
    classes = Classification.query.all()
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('index.html', classes=classes, messages=messages)

# 用户的基本信息页面
@main.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return render_template('users/user.html', user=user)
    else:
        abort(404)

# 用户的修改页面
@main.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditProfileForm()
    # pic = UploadSet('pic')
    # configure_uploads(current_app, pic)
    if form.validate_on_submit():
        if form.img.data:
            if current_user.img_src:
                img_path = current_app.config['UPLOADED_PIC_DEST']+"/"+str(current_user.id)+\
                           "/"+current_user.img_src.split("/")[-1]
                flash(current_user.img_src.split("/")[-1])
                # flash(img_path)
                if os.path.exists(img_path):
                    os.remove(img_path)
                    flash(u"删除成功")
                else:
                    flash(img_path)
            strlist = str(form.img.data.filename).split(".")
            filename = datetime.now().strftime("%Y%m%d%H%M%S") + "." + strlist[-1]
            # filename = form.username.data + "." + strlist[len(strlist) - 1]
            url = pic.save(form.img.data, folder=str(current_user.id)
                           ,name=filename)
            flash(url)
            current_user.img_src = 'pic/'+str(current_user.id)+"/"+filename
        current_user.username = form.username.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    form.username.data = current_user.username
    return render_template('users/edit_user.html', form=form)

# 博客文章显示
@main.route("/post_view/<post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    form = EditCommentForm()
    if post is not None:
        classifi = Classification.query.filter_by(id=post.class_id).first()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              post=post,
                              author=current_user._get_current_object())
            db.session.add(comment)
            flash('Your comment has been published.')
            return redirect(url_for('main.show_post', post_id=post.id, page=-1))
            # 但是在 url_for() 函数的参数中把 page 设为 -1 ,这是个特殊的页
            # 数,用来请求评论的最后一页, 这里设置每页五条评论
        page = request.args.get('page', 1, type=int)
        if page == -1:
            page = (post.comments.count() - 1) / 5 + 1
        pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
            page, per_page=5, error_out=False)
        comments = pagination.items
        return render_template('post_view.html', post=post, name=classifi.name, form=form,
                               comments=comments, pagination=pagination, Permission=Permission)
    else:
        abort(404)
    # if session.has_key('user_id'):
    #     flash(u"已登录")
    #     user = User.query.filter_by(email=current_user.email).first()
    #     if user in post.users.all():
    #         followed = True
    #     else:
    #         if followed == True:
    #             post.users.append(user)
    #             # return redirect("main.show_post", post_id=post.id, followed=followed)
    # else:
    #     followed = False
    # return render_template("post_view.html", post=post,
    #                     name=classifi.name)

# 博客文章列表
@main.route("/post_list/<class_id>", methods=['GET', 'POST'])
def show_post_list(class_id):
    classification = Classification.query.filter_by(id=class_id).first()
    if classification is not None:
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.filter_by(class_id=class_id).paginate(
            page, per_page=2, error_out=False
        )
        posts = pagination.items
        return render_template("post_list.html", classification=classification, posts=posts,
                               pagination=pagination)
    else:
        abort(404)

# 用户关注文章
@main.route("/follow/<post_id>", methods=['GET', 'POST'])
@login_required
def follow(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash(u"关注的文章不存在哦！")
        return redirect(url_for("main.index"))
    else:
        current_user.follow(post)
        return redirect(url_for("main.show_post", post_id=post.id))

# 用户取消关注
@main.route("/unfollow/<post_id>", methods=['GET', 'POST'])
@login_required
def unfollow(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        flash(u"取消关注的文章不存在哦！")
        return redirect(url_for("main.index"))
    else:
        current_user.unfollow(post)
        return redirect(url_for("main.show_post", post_id=post.id))



# @main.route("/test", methods=['GET', 'POST'])
# def test():
#     # form = SelectForm()
#     # if form.validate_on_submit():
#     #     return render_template("test.html", data=form.test.data)
#     url = './static/pic/chen2.jpg'
#     flash(url)
#     return render_template("test.html", url=url)
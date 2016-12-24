# -*- coding: utf-8 -*-
"""
Created on 16-11-21 /上午6:22
@author: Chen Jinbin
"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from .import login_manager
from flask import current_app, redirect
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from markdown import markdown
import bleach


# class Admin(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(64), unique=True)
#     username = db.Column(db.String(64), unique=True)
#     password_hash = db.Column(db.Text)
#     img_src = db.Column(db.String(64), unique=True)


# 定义博客和用户关系表
follows = db.Table('follows',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)

class User(db.Model,UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    img_src = db.Column(db.String(64), unique=True)
    # about_me = db.Column(db.Text())  # 用户自我介绍，暂时不用
    state = db.Column(db.Integer)  # 用户的状态，是否可用
    confirmed = db.Column(db.Boolean, default=False)  # 判断用户是否已进行邮箱验证
    permissions = db.Column(db.Integer, index=True)  # 标示用户权限
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 用户的注册时间 UTC为协调时间
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 用户最后的访问时间
    posts = db.relationship('Post', secondary=follows, backref=db.backref('users', lazy='dynamic'),
                                  lazy='dynamic')  # 定义多对多关系
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # 这个不懂，为什么要调用父类的构造函数
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email == current_app.config['FLASKY_ADMIN']:
            self.permissions = Permission.ADMIN
        else:
            self.permissions = Permission.USER

    # 设置权限, 此次因为只有两个权限,下面的方式可改用更简单的方法
    # 但如果有多级权限采用下列方式是个不错的选择
    def can(self, permissions):
        return self.permissions == permissions

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    # 此时传入的password应该是不可读的
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成注册确认令牌
    def generate_confirm_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm': self.id})

    # 验证令牌
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 生成重置密码令牌
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    # 生成重置邮箱令牌, 由用户id和新的邮箱地址生成
    def generate_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    # 刷新用户最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 用户关注文章
    def follow(self, post):
        if not self.is_following(post):
            self.posts.append(post)
            db.session.add(self)
            db.session.commit()

    # 取消关注
    def unfollow(self, post):
        if self.is_following(post):
            self.posts.remove(post)
            # db.session.add(self)
            # db.session.commit()
            # return "yes"

    # 表示用户已关注文章
    def is_following(self, post):
        return post in self.posts.all()

# 对匿名用户（游客）权限的处理
# 自定义匿名用户
# 这个对象继承自 Flask-Login 中的 AnonymousUserMixin 类,并将其设为用户未登录时
# current_user 的值。这样程序不用先检查用户是否登录,就能自由调用 current_user.can() 和
# current_user.is_administrator() 。
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
#
# class Follows(db.Model):
#     pass

"""
你需要提供一个 user_loader 回调。这个回调用于从会话中
存储的用户 ID 重新加载用户对象。它应该接受一个用户的 unicode ID，
并返回相应的用户对象。
如果 ID 无效，它应该返回 None （ 而不是抛出异常 ）。
（在这种情况下，ID 会 被手动从会话中移除且处理会继续。）
"""
@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))
"""
这里自定义自定义未登录处理函数，重定向到用户登录界面
"""
from flask import url_for, flash
@login_manager.unauthorized_handler
def unauthorized():
    flash(u'请先登录')
    return redirect(url_for('auth.login'))

class Permission:
    ADMIN = 6
    USER = 1

# 博客
class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True, index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    class_id = db.Column(db.Integer, db.ForeignKey('classifications.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tages = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                         'em', 'i', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2',
                         'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tages, strip=True
        ))

    def get_class_name(self):
        classification = Classification.query.filter_by(id=self.class_id).first()
        return classification.name


db.event.listen(Post.body, 'set', Post.on_changed_body)

# 博客类型
class Classification(db.Model):
    __tablename__ = "classifications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),index=True, unique=True)
    img_src = db.Column(db.String(64))
    brief = db.Column(db.Text)
    posts = db.relationship('Post', backref='class',lazy='dynamic')

# 博客评论
class Comment(db.Model):
    # 包括 id，内容，HTML格式的内容，发布时间，发布人id, 博客id
    # disabled 管理员查禁不当言论, 开始默认为False(允许评论, 其实也可以不填默认值)
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,  index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    disabled = db.Column(db.Boolean, default=False)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong', 'pre']

        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    # 获取评论的博客和用户，因为不知道有没有其他方法，暂时先这样
    # 现在找到了，直接用comment.author和comment.post直接获得，还是SQLAlchemy不会用
    def get_post(self):
        return Post.query.filter_by(id=self.post_id).first()

    def get_author(self):
        return User.query.filter_by(id=self.author_id).first()

db.event.listen(Comment.body, 'set', Comment.on_changed_body)

# 公告模型
class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    enable = db.Column(db.Boolean, default=False)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong', 'pre']

        target.content_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Message.content, 'set', Message.on_changed_body)

















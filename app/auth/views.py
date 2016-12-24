# -*- coding: utf-8 -*-
"""
Created on 16-11-22 /上午10:04
@author: Chen Jinbin
"""
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from ..models import User
from .forms import LoginForm
from .forms import RegisterForm, ChangePasswordForm, PasswordResetReqForm, ResetEmailForm
from .. import db
from flask_login import current_user
from flask import current_app
from flask_mail import Message
from ..email import send_email
from .. import mail

# 对登录之后的 用户的请求进行判断如果是已登录认证
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()  # 在用户每次访问之后，都进行时间刷新
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

# 实现用户登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template("auth/login.html", form=form)


# 实现用户登出
@auth.route('/logout', methods=['GET', 'POST'])
@login_required  # 保护路由
def logout():
    logout_user()
    flash('You have been logout')
    return redirect(url_for('main.index'))

# 实现用户注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirm_token()
        send_email(user.email, 'auth/email/confirm',
                   'Confirm Your Account', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# 邮箱验证
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

# 对未验证的登录用户
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

# 重新发送邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirm_token()
    send_email(current_user.email, 'auth/email/confirm',
                   'Confirm Your Account', user=current_user, token=token)
    flash(u'新的邮件链接已发送！')
    return redirect(url_for('main.index'))

@auth.route('/change_password')
@login_required
def change_password():
    form = ChangePasswordForm()
    change_success = False
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
                current_user.password = form.new_password.data
                db.session.add(current_user)
                change_success = True
                return redirect(url_for('auth.change_password'), change_state=change_success)
        else:
            flash(u"现有密码输入错误")
    return render_template('auth/change_password.html', change_state=False)
'''
    忘记密码功能将在登录页面中显示
'''
# 忘记密码
@auth.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = PasswordResetReqForm()
    user = User.query.filter_by(email=form.email.data).first()
    if user is not None:
        token = user.generate_reset_token()
        send_email(user.email, 'auth/email/reset_password', 'Reset your Password', token=token, user=user)
        flash(u"请登录邮箱点击链接重置密码")
        return redirect(url_for('main.index'))
    else:
        flash("The email is not invalid")
    return render_template('auth/reset_password.html', form=form)

# 重置密码
@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash(u"密码重置成功，请重新登录")
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template("auth/reset_password.html", form=form)


'''
    因为更改邮箱的功能并不常见
    所以这个功能先保留， 不在实际项目中使用
'''
# 修改邮箱，及邮件发送
@auth.route('/change_email_request')
@login_required
def change_email_request():
    form = ResetEmailForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=current_user.email).first()
        # if user is not None:
        token = current_user.generate_email_token(form.email.data)
        send_email(form.email.data, 'auth/email/change_email', u"更改邮箱地址",
                   token=token, user=current_user)
        flash(u"请在新邮箱中点击验证")
        return redirect(url_for('main.index'))
    return render_template('auth/change_mail.html', form=form)

# 新邮箱验证
@auth.route('/change_email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    if current_user.change_mail(token):
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('main.index'))
















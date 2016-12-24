#-*- coding:utf-8 -*-
from flask import Flask, render_template, redirect, request, \
    session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'mysql://root:123456@localhost:3306/fuck'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

#定义表单类
class NameForm(FlaskForm):
    #Required确保提交的字段不为空
    name = StringField('what is your name', validators=[Required()])
    submit = SubmitField('Submit')

bootstrap = Bootstrap(app)
#保护表单免受CSRF攻击, 在使用wtf时必须配置，一般写在配置文件中
app.config['SECRET_KEY'] = '1234abcd'


@app.route("/")
def index():
    return render_template("index.html")

#表单类的应用
@app.route("/formname", methods=['GET', 'POST'])
def formshow():
    #普通的请求，但在页面刷新时会弹出警告，不太好
    # name = None
    # form = NameForm()
    # if form.validate_on_submit():
    #     name = form.name.data
    #     form.name.data = ''
    # return render_template('formName.html', form=form, name=name)

    #解决 使用session和重定向
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash(u'姓名已改变')
        # 将form.name.data中的数据保存到session中
        session['name'] = form.name.data
        return redirect(url_for('formshow'))
    return render_template('formName.html', form=form, name=session.get('name'))


#重定向的应用
@app.route("/redit_user")
def redit_user():
    name = request.headers.get("User-Agent")
    return redirect("./templates/user.html")
    # return "<h1>%s</h1>" % name

#传入参数
@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

@app.route("/post/<subject>")
def post_list(subject):
    return render_template("post_list.html", subject=subject)

@app.route("/views/<post_id>")
def post_view(post_id):
    return render_template("post_view.html", post_id=post_id)

#错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(debug=True)


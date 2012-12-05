# -*- coding: utf8 -*-
import hashlib

import flask
from flask import (Blueprint, request, redirect, session,
    render_template, url_for, escape)
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form

from models import Users, Post
from utilities import login_required
     

class AdminLogin(MethodView):
    def get(self):
        if not 'uid' in session:
            return render_template('admin/login.html')
        
        else:
            return redirect(url_for('.console'))
            
    def post(self):
        username = escape(request.form['username'])
        password = escape(request.form['password'])
        passwd_md5 = hashlib.md5(password).hexdigest()
        
        is_valid = Users.check_user_passwd(username, passwd_md5)
        if is_valid:
            session['uid'] = username
            return redirect(url_for('.console'))

        else:
            error = 'Invalid credentials'

        return render_template('admin/login.html', error=error)


class AdminConsole(MethodView):
    def get(self):
        posts = Post.objects.all()
        return render_template('admin/post_list.html', posts=posts)

class AdminEditPost(MethodView):
    form = model_form(Post, 
        exclude=('created_at', 'comments'))

    def get(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        form = self.form()
        return render_template('posts/edit.html', post=post, form=form)

    def post(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        form = self.form(request.form)

        if form.validate():
            for field in ['slug', 'title', 'body']:
                post[field] = form[field].data
    
            post.save()

        return redirect(url_for('posts.list'))


admin = Blueprint('admin', __name__, template_folder='templates')
admin.add_url_rule('/admin/console', view_func=login_required(AdminConsole.as_view('console')))
admin.add_url_rule('/admin/login', view_func=AdminLogin.as_view('login'))
admin.add_url_rule('/admin/edit', view_func=login_required(AdminLogin.as_view('edit')))
admin.add_url_rule('/admin/<slug>/edit', view_func=login_required(AdminEditPost.as_view('edit')))
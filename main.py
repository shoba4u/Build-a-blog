#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

def get_posts(limit, offset):
    sql_str = ("SELECT * FROM Blog ORDER BY created DESC LIMIT " + str(limit)
        + " OFFSET " + str(offset))
    posts = db.GqlQuery(sql_str)
    return posts

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")

class MainPage(Handler):
    def get(self):
        Flag = "N"
        page = self.request.get("page")

        if page == "":
            page = 1
        else:
            page = int(page)

        posts = get_posts(5, (page - 1) * 5)

        if(posts.count(limit = 5, offset=(page*5)) > 0):
            Flag = "Y"
        self.render("main.html", posts=posts, error="", Flag=Flag, page=page)

class NewPost(Handler):
    
    def get(self):
        self.render("newpost.html", title="", body="", error="")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Blog(title = title, body = body)
            a.put()

            blog_post_id = str(a.key().id())
            self.redirect("/blog/"+ blog_post_id)
        else:
            error = "we need both a title and a body!"
            self.render("newpost.html",title=title, body=body, error=error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        blog_post = Blog.get_by_id(int(id))

        if blog_post:
            content = ("<h1>" + blog_post.title + "</h1>" + "<p>" + blog_post.body + "</p>")
            self.response.write(content)

        #self.render("post.html", blog_post = blog_post)  
        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
],  debug=True)

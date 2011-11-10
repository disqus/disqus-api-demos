
"""
comments oauth demo
~~~~~~~~~~~~~~~~~~~

After login, shows a list of the users most recent comments.

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import os
from disqusapi import DisqusAPI
from flask import Flask, redirect, url_for, request, session, \
  render_template

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
app.config.from_envvar('IDEA_SETTINGS')

# app.config.setdefault('DISQUS_SECRET', None)
# app.config.setdefault('DISQUS_PUBLIC', None)

disqus = DisqusAPI(app.config['DISQUS_SECRET'], app.config['DISQUS_PUBLIC'])

import simplejson
import urllib
import urllib2

@app.route('/oauth/authorize/')
def oauth_authorize():
    return redirect('https://disqus.com/api/oauth/2.0/authorize/?%s' % (urllib.urlencode({
        'client_id': disqus.public_key,
        'scope': 'read,write',
        'response_type': 'code',
        'redirect_uri': url_for('oauth_callback', _external=True),
    }),))

@app.route('/oauth/callback/')
def oauth_callback():
    code = request.args.get('code')
    error = request.args.get('error')
    if error or not code:
        # TODO: show error
        return redirect('/')

    req = urllib2.Request('https://disqus.com/api/oauth/2.0/access_token/', urllib.urlencode({
        'grant_type': 'authorization_code',
        'client_id': disqus.public_key,
        'client_secret': disqus.secret_key,
        'redirect_uri': url_for('oauth_callback', _external=True),
        'code': code,
    }))

    resp = urllib2.urlopen(req).read()

    data = simplejson.loads(resp)

    session['auth'] = data
    session.permanent = True

    return redirect('/')

@app.route('/login')
def show_login():
    return render_template('login.html')

@app.route('/')
def show_my_comments():
    if 'auth' not in session:
        return redirect(url_for('show_login'))

    comment_list = disqus.api.users.listPosts(access_token=session['auth']['access_token'], related=['thread', 'forum'])

    return render_template('comments.html', comment_list=comment_list, user=session['auth'])

if __name__ == '__main__':
    app.run()
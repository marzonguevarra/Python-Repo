try:
    from flask import Flask, render_template, url_for, redirect, session
    from authlib.integrations.flask_client import OAuth
    from datetime import timedelta
    import os
    import json
    from dotenv import load_dotenv

    # decorator for routes that should be accessible only by logged in users
    from required import login_required

except Exception as e:
    print("Some Modules are Missing : {} ".format(e))

# App config
app = Flask(__name__)
load_dotenv()

#session config
app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)

# Google oAuth2
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


def isLoggedIN():
    try:
        user = dict(session).get('profile', None)
        picture = dict(session).get('profile', None)
        if user:
            return True, user.get("name"), picture.get("picture")
        else:
            return False,{}
    except Exception as e:
        return False,{}

@app.route('/')
@app.route('/index')
def index():
   return render_template('index.html')

@app.route('/login')
def login():
     return render_template('login.html')

@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

# Google login route
@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

# Google authorize route
@app.route('/login/google/authorize')
def google_authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    picture = oauth.google.userinfo()
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed    
    return redirect('/external')
    
# external route
@app.route('/external')
@login_required
def external():
    flag,user,picture = isLoggedIN()
    return render_template('./external/home.html', flag=flag, user=user, picture=picture)

if __name__ == "__main__":
    app.run(debug=True)

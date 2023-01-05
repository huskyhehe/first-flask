import functools

from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Register a new user.
# Validates that the username is not already taken. Hashes the password for security.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate that username and password are not empty.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # If validation succeeds, insert the new user data into the database.
        if error is None:
            # try to store the user
            try:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password)),
                )
                db.commit()
            # check if the username already exists
            except db.IntegrityError:
                error = f"User {username} is already registered."
            # redirect to the login page.
            else:
                return redirect(url_for("auth.login"))

        # If validation fails, the error is shown to the user.
        flash(error)

    # When the user initially navigates to auth/register, or there was a validation error,
    # an HTML page with the registration form should be shown
    return render_template('auth/register.html')

    '''
    @bp.route 
    associates the URL /register with the register view function. 
    When Flask receives a request to /auth/register, 
    it will call the register view and use the return value as the response.
    '''
    '''
    If the user submitted the form, request.method will be 'POST'. 
    In this case, start validating the input.
    '''
    '''
    request.form 
    is a special type of dict mapping submitted form keys and values. 
    The user will input their username and password.
    '''
    '''
    db.execute 
    takes a SQL query with ? placeholders for any user input, 
    and a tuple of values to replace the placeholders with. 
    The database library will take care of escaping the values so you are not vulnerable to a SQL injection attack.
    '''
    '''
    For security, passwords should never be stored in the database directly. 
    Instead, generate_password_hash() is used to securely hash the password, 
    and that hash is stored. 
    Since this query modifies data, db.commit() needs to be called afterwards to save the changes.
    '''
    '''
    sqlite3.IntegrityError 
    will occur if the username already exists, 
    which should be shown to the user as another validation error.
    '''
    '''
    url_for() 
    generates the URL for the login view based on its name. 
    This is preferable to writing the URL directly as it allows you to 
    change the URL later without changing all code that links to it. 
    redirect() generates a redirect response to the generated URL.
    '''
    '''
    flash() 
    stores messages that can be retrieved when rendering the template.
    '''


# Log in a registered user by adding the user id to the session.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # store session, which will be available on subsequent requests.
            session.clear()
            session['user_id'] = user['id']

            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

    '''
    fetchone() 
    returns one row from the query. 
    If the query returned no results, it returns None. 
    '''
    '''
    check_password_hash() 
    hashes the submitted password in the same way as the stored hash and securely compares them. 
    If they match, the password is valid.
    '''
    '''
    session is a dict that stores data across requests. 
    When validation succeeds, the user’s id is stored in a new session. 
    The data is stored in a cookie that is sent to the browser, 
    and the browser then sends it back with subsequent requests. 
    Flask securely signs the data so that it can’t be tampered with.
    '''
    '''
    Now that the user’s id is stored in the session, 
    it will be available on subsequent requests. 
    At the beginning of each request, if a user is logged in 
    their information should be loaded and made available to other views.
    '''


#  If a user id is stored in the session, load the user object from the database.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

    '''
    bp.before_app_request() 
    registers a function that runs before the view function, 
    no matter what URL is requested. 
    
    load_logged_in_user 
    checks if a user id is stored in the session and gets that user’s data from the database, 
    storing it on g.user, which lasts for the length of the request. 
    If there is no user id, or if the id doesn’t exist, g.user will be None.
    '''


# Clear the current session, including the stored user id.
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# View decorator that redirects anonymous users to the login page.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

    '''
    Creating, editing, and deleting blog posts will require a user to be logged in. 
    A decorator can be used to check this for each view it’s applied to.
    '''
    '''
    This decorator returns a new view function that wraps the original view it’s applied to. 
    The new function checks if a user is loaded and redirects to the login page otherwise. 
    If a user is loaded the original view is called and continues normally. 
    You’ll use this decorator when writing the blog views.
    '''
    '''
     url_for() 
     function generates the URL to a view based on a name and arguments. 
     The name associated with a view is also called the endpoint, 
     and by default it’s the same as the name of the view function.
    '''

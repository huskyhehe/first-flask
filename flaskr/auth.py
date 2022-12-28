from flask import Blueprint, request, redirect, url_for, flash, render_template
from werkzeug.security import generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


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
                    "INSERT INTO user (username, password) VALUES (?, ?)"
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

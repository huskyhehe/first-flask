from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, g

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


# Show all the posts, most recent first.
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created_at, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created_at DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# Get a post and its author by id.
def get_post(id, check_author=True):
    """
    param id: id of post to get
    param check_author: require the current user to be the author
    return: the post with author information
    raise 404: if a post with the given id doesn't exist
    raise 403: if the current user isn't the author
    """
    post = get_db().execute(
        'SELECT p.id, title, body, created_at, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# Create a new post for the current user.
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

    '''
    The login_required decorator you wrote earlier is used on the blog views. 
    A user must be logged in to visit these views, otherwise they will be redirected to the login page.
    '''


# Update a post if the current user is the author.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# Delete a post.
# Ensures that the post exists and that the logged-in user is the author of the post.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.excute(
        'DELETE FROM post WHERE id = ?', (id, )
    )
    db.commit()
    return redirect(url_for('blog.index'))

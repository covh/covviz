import os

from bottle import route, template, redirect, static_file, error, run


@route('/home')
def show_home():
    return template('home')


@route('/')
def handle_root_url():
    redirect('/home')


@route('/csvtest')
def make_request():
    # make an API request here
    data="test123"
    return template('csvtest', output=data)


@route('/css/<filename>')
def send_css(filename):
    return static_file(filename, root='static/css')


@error(404)
def error404(error):
    return template('error', error_msg='404 error. Nothing to see here')


if "heroku" in os.environ.get('PYTHONHOME', ''):
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=8080, debug=True)

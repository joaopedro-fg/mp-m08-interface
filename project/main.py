from flask import Blueprint, render_template, request
from . import db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')
    
@main.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == 'POST':
        print(request.form['info3'])
    return render_template('profile.html', name=current_user.name) 
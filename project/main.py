from flask import Blueprint, render_template, request, jsonify
from . import db
from . import dialog
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/log')
@login_required
def funcao_teste():
    #path hardcoded, substituir ao texto na máquina individual
    f = open("./demofile.txt", "r")
    a = f.read().splitlines()
    log_str = ""
    for log in a:
        log_str += log
        log_str +="<br>"
    f.close()
    return log_str

@main.route('/SOdialog')
@login_required
def SOdialog():
    path = dialog._open_dialog_file()
    return jsonify(path=path)

@main.route('/new_analysis', methods=['POST', 'GET'])
@login_required
def new_analysis():
    if request.method == 'POST':
        print(request.form['info3'])
    return render_template('new_analysis.html', name=current_user.name)

@main.route('/search_analysis', methods=['POST', 'GET'])
@login_required
def search_analysis():
    return render_template('search_analysis.html')
@main.route('/report', methods=['POST', 'GET'])
@login_required
def report():
    return render_template('report.html', name=current_user.name, id_report="123456", path="teste/teste/teste")
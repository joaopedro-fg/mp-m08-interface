from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from . import db
from . import dialog
from flask_login import login_required, current_user
from flask import Flask, make_response, request, session, render_template, send_file, Response
from flask.views import MethodView
from werkzeug.utils import secure_filename
from datetime import datetime
import humanize
import os
import re
import stat
import json
import mimetypes
import sys
from pathlib2 import Path

main = Blueprint('main', __name__)
global_path = 'Caminho do Diretório'
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
@main.route('/set_new_analysis', methods=['POST', 'GET'])
@login_required
def set_new_analysis():
    global global_path
    path_name = request.args.get('path_name')
    global_path = path_name
    return render_template('new_analysis.html', name=current_user.name)

@main.route('/new_analysis', methods=['POST', 'GET'])
@login_required
def new_analysis():
    if request.method == 'POST':
        print(request.form['info3'])
    return render_template('new_analysis.html', name=current_user.name)

@main.route('/search_analysis', methods=['POST', 'GET'])
@login_required
def search_analysis():
    return render_template('search_analysis.html', name=current_user.name, id_process=1, buffer='log_obj.buffer',  
                                                   conf_nsfw='conf', conf_face='conf', 
                                                   conf_child='conf', conf_age='conf')
@main.route('/set_analysis', methods=['POST', 'GET'])
@login_required
def set_analysis():
    #global log_obj
    #global id_process

    analysis_path = request.args.get('path_name')
    '''
    if analysis_path is not None and analysis_path != '' and isinstance(analysis_path, str):
        log_obj.send(('imprime', 
                      '{1} - [{0}] Importando dados de análise'.format(current_user.name,
                                                                     datetime.now().strftime("%d/%m/%Y %H:%M:%S")) 
                     ))
        
        idx = analysis_path.rfind('.')
        id_process = os.path.basename(analysis_path[:idx])
        log_obj.set_id(id_process, search=True)
        return jsonify(id_process=id_process)
        
    flash('Erro ao carregar arquivo.'.format(id_process), 'error')
    '''
    print(analysis_path)
    return redirect(url_for('main.search_analysis')) 
@main.route('/report', methods=['POST', 'GET'])
@login_required
def report():
    return render_template('report.html', name=current_user.name, id_report="123456", path="teste/teste/teste")
# Código do sistema de arquivos começa aqui
root = os.path.normpath(os.getenv('FS_PATH', ''))
key = os.getenv('FS_KEY')

ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg', '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX', 'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']
datatypes = {'audio': 'm4a,mp3,oga,ogg,webma,wav', 'archive': '7z,zip,rar,gz,tar', 'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'pdf': 'pdf', 'quicktime': '3g2,3gp,3gp2,3gpp,mov,qt', 'source': 'atom,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml,plist', 'text': 'txt', 'video': 'mp4,m4v,ogv,webm', 'website': 'htm,html,mhtm,mhtml,xhtm,xhtml'}
icontypes = {'fa-music': 'm4a,mp3,oga,ogg,webma,wav', 'fa-archive': '7z,zip,rar,gz,tar', 'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'fa-file-text': 'pdf', 'fa-film': '3g2,3gp,3gp2,3gpp,mov,qt', 'fa-code': 'atom,plist,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml', 'fa-file-text-o': 'txt', 'fa-film': 'mp4,m4v,ogv,webm', 'fa-globe': 'htm,html,mhtm,mhtml,xhtm,xhtml'}

@main.app_template_filter('size_fmt')
def size_fmt(size):
    return humanize.naturalsize(size)

@main.app_template_filter('time_fmt')
def time_desc(timestamp):
    mdate = datetime.fromtimestamp(timestamp)
    str = mdate.strftime('%Y-%m-%d %H:%M:%S')
    return str

@main.app_template_filter('data_fmt')
def data_fmt(filename):
    t = 'unknown'
    for type, exts in datatypes.items():
        if filename.split('.')[-1] in exts:
            t = type
    return t

@main.app_template_filter('icon_fmt')
def icon_fmt(filename):
    i = 'fa-file-o'
    for icon, exts in icontypes.items():
        if filename.split('.')[-1] in exts:
            i = icon
    return i

@main.app_template_filter('humanize')
def time_humanize(timestamp):
    mdate = datetime.utcfromtimestamp(timestamp)
    return humanize.naturaltime(mdate)

def get_type(mode):
    if stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        type = 'dir'
    else:
        type = 'file'
    return type

def partial_response(path, start, end=None):
    file_size = os.path.getsize(path)

    if end is None:
        end = file_size - start - 1
    end = min(end, file_size - 1)
    length = end - start + 1

    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    return response

def get_range(request):
    range = request.headers.get('Range')
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None

class PathView(MethodView):
    def get(self, p=''):
        hide_dotfile = request.args.get('hide-dotfile', request.cookies.get('hide-dotfile', 'no'))

        path = os.path.join(root, p)

        if os.path.isdir(path):
            contents = []
            total = {'size': 0, 'dir': 0, 'file': 0}
            for filename in os.listdir(path):
                if filename in ignored:
                    continue
                if hide_dotfile == 'yes' and filename[0] == '.':
                    continue
                filepath = os.path.join(path, filename)
                stat_res = os.stat(filepath)
                info = {}
                info['name'] = filename
                info['mtime'] = stat_res.st_mtime
                ft = get_type(stat_res.st_mode)
                info['type'] = ft
                total[ft] += 1
                sz = stat_res.st_size
                info['size'] = sz
                total['size'] += sz
                contents.append(info)
            page = render_template('busca_arquivo.html', path=p, contents=contents, total=total, hide_dotfile=hide_dotfile,real_path=path)
            res = make_response(page, 200)
            res.set_cookie('hide-dotfile', hide_dotfile, max_age=16070400)
        elif os.path.isfile(path):
            if 'Range' in request.headers:
                start, end = get_range(request)
                res = partial_response(path, start, end)
            else:
                res = send_file(path)
                res.headers.add('Content-Disposition', 'attachment')
        else:
            res = make_response('Not found', 404)
        return res
    
    def put(self, p=''):
        if request.cookies.get('auth_cookie') == key:
            path = os.path.join(root, p)
            dir_path = os.path.dirname(path)
            Path(dir_path).mkdir(parents=True, exist_ok=True)

            info = {}
            if os.path.isdir(dir_path):
                try:
                    filename = secure_filename(os.path.basename(path))
                    with open(os.path.join(dir_path, filename), 'wb') as f:
                        f.write(request.stream.read())
                except Exception as e:
                    info['status'] = 'error'
                    info['msg'] = str(e)
                else:
                    info['status'] = 'success'
                    info['msg'] = 'File Saved'
            else:
                info['status'] = 'error'
                info['msg'] = 'Invalid Operation'
            res = make_response(json.JSONEncoder().encode(info), 201)
            res.headers.add('Content-type', 'application/json')
        else:
            info = {} 
            info['status'] = 'error'
            info['msg'] = 'Authentication failed'
            res = make_response(json.JSONEncoder().encode(info), 401)
            res.headers.add('Content-type', 'application/json')
        return res

    def post(self, p=''):
        if request.cookies.get('auth_cookie') == key:
            path = os.path.join(root, p)
            Path(path).mkdir(parents=True, exist_ok=True)

            info = {}
            if os.path.isdir(path):
                files = request.files.getlist('files[]')
                for file in files:
                    try:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(path, filename))
                    except Exception as e:
                        info['status'] = 'error'
                        info['msg'] = str(e)
                    else:
                        info['status'] = 'success'
                        info['msg'] = 'File Saved'
            else:
                info['status'] = 'error'
                info['msg'] = 'Invalid Operation'
            res = make_response(json.JSONEncoder().encode(info), 200)
            res.headers.add('Content-type', 'application/json')
        else:
            info = {} 
            info['status'] = 'error'
            info['msg'] = 'Authentication failed'
            res = make_response(json.JSONEncoder().encode(info), 401)
            res.headers.add('Content-type', 'application/json')
        return res
    
    def delete(self, p=''):
        if request.cookies.get('auth_cookie') == key:
            path = os.path.join(root, p)
            dir_path = os.path.dirname(path)
            Path(dir_path).mkdir(parents=True, exist_ok=True)

            info = {}
            if os.path.isdir(dir_path):
                try:
                    filename = secure_filename(os.path.basename(path))
                    os.remove(os.path.join(dir_path, filename))
                    os.rmdir(dir_path)
                except Exception as e:
                    info['status'] = 'error'
                    info['msg'] = str(e)
                else:
                    info['status'] = 'success'
                    info['msg'] = 'File Deleted'
            else:
                info['status'] = 'error'
                info['msg'] = 'Invalid Operation'
            res = make_response(json.JSONEncoder().encode(info), 204)
            res.headers.add('Content-type', 'application/json')
        else:
            info = {}
            info['status'] = 'error'
            info['msg'] = 'Authentication failed'
            res = make_response(json.JSONEncoder().encode(info), 401)
            res.headers.add('Content-type', 'application/json')
        return res

path_view = PathView.as_view('path_view')
main.add_url_rule('/arquivos', view_func=path_view)
main.add_url_rule('/<path:p>', view_func=path_view)
#Código do sistema de arquivos termina aqui
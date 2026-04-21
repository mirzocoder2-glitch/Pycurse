"""
ПлатформаТЈ — Flask Backend
Сохтор:
  app.py
  requirements.txt
  templates/
    style.css      <- CSS
    api.js         <- JS
    index.html
    login.html
    admin.html
    ... (ҳамаи HTML)
  instance/
    platform.db    <- SQLite база (худкор месозад)
  uploads/
    videos/        <- Видеофайлҳо
"""

from flask import (Flask, request, jsonify, send_from_directory,
                   session, render_template)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, json
from datetime import datetime
from functools import wraps

# ===== APP =====
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'platformtj-dev-2024')
CORS(app, supports_credentials=True)

UPLOAD_DIR = os.path.join('uploads', 'videos')
DB_PATH    = os.path.join('instance', 'platform.db')
ALLOWED    = {'mp4', 'webm', 'avi', 'mov', 'mkv'}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs('instance', exist_ok=True)


# ===== CSS, JS ВА ДИГАР ФАЙЛҲО АЗ templates/ =====
@app.route('/style.css')
def serve_css():
    return send_from_directory('templates', 'style.css')

@app.route('/api.js')
def serve_js():
    return send_from_directory('templates', 'api.js')


# ===== СТРАНИЦАҲО =====
@app.route('/')
def page_index():        return render_template('index.html')

@app.route('/login.html')
@app.route('/login')
def page_login():        return render_template('login.html')

@app.route('/admin.html')
@app.route('/admin')
def page_admin():        return render_template('admin.html')

@app.route('/dashboard.html')
@app.route('/dashboard')
def page_dashboard():    return render_template('dashboard.html')

@app.route('/pupil.html')
@app.route('/pupil')
def page_pupil():        return render_template('pupil.html')

@app.route('/test.html')
@app.route('/test')
def page_test():         return render_template('test.html')

@app.route('/zadacha.html')
@app.route('/zadacha')
def page_zadacha():      return render_template('zadacha.html')

@app.route('/reyting.html')
@app.route('/reyting')
def page_reyting():      return render_template('reyting.html')

@app.route('/chat.html')
@app.route('/chat')
def page_chat():         return render_template('chat.html')

@app.route('/jadval.html')
@app.route('/jadval')
def page_jadval():       return render_template('jadval.html')

@app.route('/sertifikat.html')
@app.route('/sertifikat')
def page_sertifikat():   return render_template('sertifikat.html')

@app.route('/interpretator.html')
@app.route('/interpretator')
def page_interpretator(): return render_template('interpretator.html')


# ===== DATABASE =====
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db

def row2dict(r):  return dict(r) if r else None
def rows2list(r): return [dict(x) for x in r]

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT DEFAULT '',
        role TEXT DEFAULT 'student',
        avatar TEXT DEFAULT '👨‍🎓',
        points INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        icon TEXT DEFAULT '📚',
        level TEXT DEFAULT 'Ибтидоӣ',
        duration TEXT DEFAULT '',
        category TEXT DEFAULT 'programming',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        order_num INTEGER DEFAULT 1,
        video_name TEXT DEFAULT '',
        video_path TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        time_limit INTEGER DEFAULT 30,
        questions TEXT DEFAULT '[]',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        difficulty TEXT DEFAULT 'easy',
        language TEXT DEFAULT 'python',
        starter_code TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        test_id INTEGER NOT NULL,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        percent INTEGER DEFAULT 0,
        date TEXT DEFAULT (datetime('now')),
        UNIQUE(user_id, test_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (test_id)  REFERENCES tests(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        type TEXT DEFAULT 'lesson',
        day_of_week INTEGER DEFAULT 1,
        time TEXT DEFAULT '09:00',
        duration INTEGER DEFAULT 60,
        repeat TEXT DEFAULT 'weekly',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        icon TEXT DEFAULT '🔔',
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    # Admin
    if not db.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        db.execute("INSERT INTO users (name,username,password,role,avatar) VALUES (?,?,?,?,?)",
            ('Администратор','admin',generate_password_hash('admin123'),'admin','👨‍💼'))
    # Demo student
    if not db.execute("SELECT 1 FROM users WHERE username='student1'").fetchone():
        db.execute("INSERT INTO users (name,username,password,role,avatar,points) VALUES (?,?,?,?,?,?)",
            ('Алишер Раҳимов','student1',generate_password_hash('pass123'),'student','👨‍🎓',850))
    # Demo course
    if not db.execute("SELECT 1 FROM courses LIMIT 1").fetchone():
        db.execute("INSERT INTO courses (title,description,icon,level,duration,category) VALUES (?,?,?,?,?,?)",
            ('Асосҳои Python','Барномасозии Python аз сифр то касбӣ.','🐍','Ибтидоӣ','40 соат','programming'))
    db.commit(); db.close()


# ===== AUTH DECORATORS =====
def login_required(f):
    @wraps(f)
    def dec(*a,**k):
        if 'user_id' not in session:
            return jsonify({'error':'Дохил нашудаед'}),401
        return f(*a,**k)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a,**k):
        if 'user_id' not in session:
            return jsonify({'error':'Дохил нашудаед'}),401
        if session.get('role')!='admin':
            return jsonify({'error':'Ҳуқуқ нест'}),403
        return f(*a,**k)
    return dec

def allowed_video(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED


# =====================================================
# AUTH API
# =====================================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    d = request.get_json()
    u = (d.get('username') or '').strip()
    p = d.get('password') or ''
    if not u or not p:
        return jsonify({'error':'Логин ва парол ҳатмӣ!'}),400
    db   = get_db()
    user = row2dict(db.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone())
    db.close()
    if not user or not check_password_hash(user['password'],p):
        return jsonify({'error':'Логин ё парол нодуруст!'}),401
    session.update(user_id=user['id'],role=user['role'],name=user['name'])
    user.pop('password',None)
    return jsonify({'success':True,'user':user})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success':True})

@app.route('/api/auth/me')
@login_required
def me():
    db   = get_db()
    user = row2dict(db.execute(
        "SELECT id,name,username,email,role,avatar,points,created_at FROM users WHERE id=?",
        (session['user_id'],)).fetchone())
    db.close()
    return jsonify(user)


# =====================================================
# USERS API
# =====================================================
@app.route('/api/users')
@login_required
def get_users():
    db = get_db()
    us = rows2list(db.execute(
        "SELECT id,name,username,email,role,avatar,points,created_at FROM users ORDER BY id"
    ).fetchall())
    db.close(); return jsonify(us)

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    d = request.get_json()
    if not all([d.get('name'),d.get('username'),d.get('password')]):
        return jsonify({'error':'Ном, логин, парол ҳатмӣ!'}),400
    av = '👨‍💼' if d.get('role')=='admin' else '👨‍🎓'
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (name,username,password,email,role,avatar) VALUES (?,?,?,?,?,?)",
            (d['name'],d['username'],generate_password_hash(d['password']),
             d.get('email',''),d.get('role','student'),av))
        db.commit()
        u = row2dict(db.execute(
            "SELECT id,name,username,email,role,avatar,points,created_at FROM users WHERE id=?",
            (cur.lastrowid,)).fetchone())
        db.close(); return jsonify(u),201
    except sqlite3.IntegrityError:
        db.close(); return jsonify({'error':'Ин логин аллакай мавҷуд аст!'}),409

@app.route('/api/users/<int:uid>', methods=['PUT'])
@admin_required
def update_user(uid):
    d = request.get_json()
    db = get_db()
    flds,vals=[],[]
    for col in ('name','username','email','role','avatar','points'):
        if col in d: flds.append(f"{col}=?"); vals.append(d[col])
    if d.get('password'): flds.append("password=?"); vals.append(generate_password_hash(d['password']))
    if not flds: db.close(); return jsonify({'error':'Тағйирот нест'}),400
    vals.append(uid)
    db.execute(f"UPDATE users SET {','.join(flds)} WHERE id=?",vals)
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/users/<int:uid>', methods=['DELETE'])
@admin_required
def delete_user(uid):
    if uid==1: return jsonify({'error':'Супер-админро ҳазф кардан мумкин нест!'}),403
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?",(uid,))
    db.commit(); db.close(); return jsonify({'success':True})


# =====================================================
# COURSES API
# =====================================================
@app.route('/api/courses')
def get_courses():
    db = get_db()
    cs = rows2list(db.execute("SELECT * FROM courses ORDER BY id").fetchall())
    for c in cs:
        c['lessons'] = db.execute(
            "SELECT COUNT(*) FROM topics WHERE course_id=?",(c['id'],)).fetchone()[0]
    db.close(); return jsonify(cs)

@app.route('/api/courses', methods=['POST'])
@admin_required
def create_course():
    d = request.get_json()
    if not d.get('title'): return jsonify({'error':'Ном ҳатмӣ!'}),400
    db  = get_db()
    cur = db.execute(
        "INSERT INTO courses (title,description,icon,level,duration,category) VALUES (?,?,?,?,?,?)",
        (d['title'],d.get('description',''),d.get('icon','📚'),
         d.get('level','Ибтидоӣ'),d.get('duration',''),d.get('category','programming')))
    db.commit()
    c = row2dict(db.execute("SELECT * FROM courses WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(c),201

@app.route('/api/courses/<int:cid>', methods=['PUT'])
@admin_required
def update_course(cid):
    d = request.get_json()
    db = get_db()
    db.execute("UPDATE courses SET title=?,description=?,icon=?,level=?,duration=?,category=? WHERE id=?",
        (d.get('title'),d.get('description',''),d.get('icon','📚'),
         d.get('level','Ибтидоӣ'),d.get('duration',''),d.get('category','programming'),cid))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/courses/<int:cid>', methods=['DELETE'])
@admin_required
def delete_course(cid):
    db = get_db()
    for t in rows2list(db.execute("SELECT video_path FROM topics WHERE course_id=?",(cid,)).fetchall()):
        if t['video_path'] and os.path.exists(t['video_path']): os.remove(t['video_path'])
    db.execute("DELETE FROM courses WHERE id=?",(cid,))
    db.commit(); db.close(); return jsonify({'success':True})


# =====================================================
# TOPICS API
# =====================================================
@app.route('/api/topics')
@login_required
def get_topics():
    cid = request.args.get('course_id')
    db  = get_db()
    ts  = rows2list(db.execute(
        "SELECT * FROM topics WHERE course_id=? ORDER BY order_num" if cid
        else "SELECT * FROM topics ORDER BY course_id,order_num",
        (cid,) if cid else ()).fetchall())
    db.close()
    for t in ts: t.pop('video_path',None)
    return jsonify(ts)

@app.route('/api/topics', methods=['POST'])
@admin_required
def create_topic():
    title = request.form.get('title','').strip()
    cid   = request.form.get('course_id',type=int)
    desc  = request.form.get('description','')
    order = request.form.get('order_num',1,type=int)
    if not title or not cid: return jsonify({'error':'Унвон ва курс ҳатмӣ!'}),400
    vn,vp='',''
    if 'video' in request.files:
        f = request.files['video']
        if f and f.filename and allowed_video(f.filename):
            fn = secure_filename(f.filename)
            un = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fn}"
            vp = os.path.join(UPLOAD_DIR,un); f.save(vp); vn=fn
    db  = get_db()
    cur = db.execute(
        "INSERT INTO topics (course_id,title,description,order_num,video_name,video_path) VALUES (?,?,?,?,?,?)",
        (cid,title,desc,order,vn,vp))
    db.commit()
    t = row2dict(db.execute("SELECT * FROM topics WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); t.pop('video_path',None); return jsonify(t),201

@app.route('/api/topics/<int:tid>', methods=['PUT'])
@admin_required
def update_topic(tid):
    db  = get_db()
    old = row2dict(db.execute("SELECT * FROM topics WHERE id=?",(tid,)).fetchone())
    if not old: db.close(); return jsonify({'error':'Ёфт нашуд'}),404
    vn,vp = old['video_name'],old['video_path']
    if 'video' in request.files:
        f = request.files['video']
        if f and f.filename and allowed_video(f.filename):
            if vp and os.path.exists(vp): os.remove(vp)
            fn=secure_filename(f.filename)
            un=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fn}"
            vp=os.path.join(UPLOAD_DIR,un); f.save(vp); vn=fn
    db.execute("UPDATE topics SET title=?,description=?,order_num=?,course_id=?,video_name=?,video_path=? WHERE id=?",
        (request.form.get('title',old['title']),request.form.get('description',old['description']),
         request.form.get('order_num',old['order_num'],type=int),
         request.form.get('course_id',old['course_id'],type=int),vn,vp,tid))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/topics/<int:tid>', methods=['DELETE'])
@admin_required
def delete_topic(tid):
    db = get_db()
    t  = row2dict(db.execute("SELECT video_path FROM topics WHERE id=?",(tid,)).fetchone())
    if t and t['video_path'] and os.path.exists(t['video_path']): os.remove(t['video_path'])
    db.execute("DELETE FROM topics WHERE id=?",(tid,))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/topics/<int:tid>/video')
@login_required
def stream_video(tid):
    db = get_db()
    t  = row2dict(db.execute("SELECT video_path FROM topics WHERE id=?",(tid,)).fetchone())
    db.close()
    if not t or not t['video_path']: return jsonify({'error':'Видео нест'}),404
    d  = os.path.dirname(os.path.abspath(t['video_path']))
    fn = os.path.basename(t['video_path'])
    return send_from_directory(d,fn,conditional=True)


# =====================================================
# TESTS API
# =====================================================
@app.route('/api/tests')
@login_required
def get_tests():
    cid = request.args.get('course_id')
    db  = get_db()
    ts  = rows2list(db.execute(
        "SELECT * FROM tests WHERE course_id=? ORDER BY id" if cid
        else "SELECT * FROM tests ORDER BY id",
        (cid,) if cid else ()).fetchall())
    db.close()
    for t in ts:
        t['questions']=json.loads(t['questions'])
        if session.get('role')!='admin':
            for q in t['questions']: q.pop('correct',None)
    return jsonify(ts)

@app.route('/api/tests', methods=['POST'])
@admin_required
def create_test():
    d = request.get_json()
    if not d.get('title') or not d.get('course_id'):
        return jsonify({'error':'Унвон ва курс ҳатмӣ!'}),400
    db  = get_db()
    cur = db.execute(
        "INSERT INTO tests (course_id,title,description,time_limit,questions) VALUES (?,?,?,?,?)",
        (d['course_id'],d['title'],d.get('description',''),
         d.get('time_limit',30),json.dumps(d.get('questions',[]))))
    db.commit()
    t = row2dict(db.execute("SELECT * FROM tests WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); t['questions']=json.loads(t['questions']); return jsonify(t),201

@app.route('/api/tests/<int:tid>', methods=['PUT'])
@admin_required
def update_test(tid):
    d = request.get_json(); db = get_db()
    db.execute("UPDATE tests SET title=?,description=?,course_id=?,time_limit=?,questions=? WHERE id=?",
        (d['title'],d.get('description',''),d['course_id'],
         d.get('time_limit',30),json.dumps(d.get('questions',[])),tid))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/tests/<int:tid>', methods=['DELETE'])
@admin_required
def delete_test(tid):
    db = get_db()
    db.execute("DELETE FROM tests WHERE id=?",(tid,))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/tests/<int:tid>/submit', methods=['POST'])
@login_required
def submit_test(tid):
    answers = request.get_json().get('answers',{})
    db   = get_db()
    test = row2dict(db.execute("SELECT * FROM tests WHERE id=?",(tid,)).fetchone())
    if not test: db.close(); return jsonify({'error':'Тест ёфт нашуд'}),404
    qs    = json.loads(test['questions'])
    score = sum(1 for q in qs if str(q['id']) in answers
                and int(answers[str(q['id'])])==int(q.get('correct',-1)))
    total   = len(qs)
    percent = round(score/total*100) if total else 0
    uid     = session['user_id']
    db.execute("""INSERT INTO results (user_id,test_id,score,total,percent) VALUES (?,?,?,?,?)
        ON CONFLICT(user_id,test_id) DO UPDATE SET
        score=excluded.score,total=excluded.total,percent=excluded.percent,date=datetime('now')""",
        (uid,tid,score,total,percent))
    db.execute("UPDATE users SET points=points+? WHERE id=?",(score*10,uid))
    db.execute("INSERT INTO notifications (user_id,message,icon) VALUES (?,?,?)",
        (uid,f"Тест гузашт: {test['title']} — {percent}%",'📝'))
    db.commit(); db.close()
    return jsonify({'score':score,'total':total,'percent':percent,'points_earned':score*10})


# =====================================================
# TASKS API
# =====================================================
@app.route('/api/tasks')
@login_required
def get_tasks():
    cid = request.args.get('course_id'); db = get_db()
    ts  = rows2list(db.execute(
        "SELECT * FROM tasks WHERE course_id=? ORDER BY id" if cid
        else "SELECT * FROM tasks ORDER BY id",
        (cid,) if cid else ()).fetchall())
    db.close(); return jsonify(ts)

@app.route('/api/tasks', methods=['POST'])
@admin_required
def create_task():
    d = request.get_json()
    if not d.get('title') or not d.get('course_id'):
        return jsonify({'error':'Унвон ва курс ҳатмӣ!'}),400
    db  = get_db()
    cur = db.execute(
        "INSERT INTO tasks (course_id,title,description,difficulty,language,starter_code) VALUES (?,?,?,?,?,?)",
        (d['course_id'],d['title'],d.get('description',''),
         d.get('difficulty','easy'),d.get('language','python'),d.get('starter_code','')))
    db.commit()
    t = row2dict(db.execute("SELECT * FROM tasks WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(t),201

@app.route('/api/tasks/<int:tid>', methods=['PUT'])
@admin_required
def update_task(tid):
    d = request.get_json(); db = get_db()
    db.execute("UPDATE tasks SET title=?,description=?,course_id=?,difficulty=?,language=?,starter_code=? WHERE id=?",
        (d['title'],d.get('description',''),d['course_id'],
         d.get('difficulty','easy'),d.get('language','python'),d.get('starter_code',''),tid))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/tasks/<int:tid>', methods=['DELETE'])
@admin_required
def delete_task(tid):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?",(tid,))
    db.commit(); db.close(); return jsonify({'success':True})


# =====================================================
# RESULTS / LEADERBOARD / ANALYTICS
# =====================================================
@app.route('/api/results')
@login_required
def get_results():
    uid = session['user_id'] if session.get('role')!='admin' \
          else request.args.get('user_id',session['user_id'])
    db  = get_db()
    res = rows2list(db.execute(
        "SELECT * FROM results WHERE user_id=? ORDER BY date DESC",(uid,)).fetchall())
    db.close(); return jsonify(res)

@app.route('/api/results/all')
@admin_required
def get_all_results():
    db  = get_db()
    res = rows2list(db.execute("""
        SELECT r.*,u.name as user_name,t.title as test_title
        FROM results r JOIN users u ON r.user_id=u.id JOIN tests t ON r.test_id=t.id
        ORDER BY r.date DESC LIMIT 200""").fetchall())
    db.close(); return jsonify(res)

@app.route('/api/leaderboard')
@login_required
def leaderboard():
    db = get_db()
    us = rows2list(db.execute("""
        SELECT id,name,avatar,points,
          (SELECT COUNT(*) FROM results WHERE user_id=users.id) as test_count,
          (SELECT COALESCE(AVG(percent),0) FROM results WHERE user_id=users.id) as avg_percent
        FROM users WHERE role='student' ORDER BY points DESC""").fetchall())
    db.close()
    for i,u in enumerate(us): u['rank']=i+1; u['avg_percent']=round(u['avg_percent'])
    return jsonify(us)

@app.route('/api/analytics')
@admin_required
def analytics():
    db = get_db()
    d  = {
        'total_users':    db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        'total_students': db.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0],
        'total_courses':  db.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
        'total_topics':   db.execute("SELECT COUNT(*) FROM topics").fetchone()[0],
        'total_tests':    db.execute("SELECT COUNT(*) FROM tests").fetchone()[0],
        'total_tasks':    db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
        'total_results':  db.execute("SELECT COUNT(*) FROM results").fetchone()[0],
        'avg_score':      round(db.execute("SELECT COALESCE(AVG(percent),0) FROM results").fetchone()[0]),
        'passed_count':   db.execute("SELECT COUNT(*) FROM results WHERE percent>=60").fetchone()[0],
        'total_messages': db.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
    }
    db.close(); return jsonify(d)


# =====================================================
# CHAT API
# =====================================================
ROOMS = [
    {'id':'general','name':'Умумӣ','icon':'💬'},
    {'id':'python', 'name':'Python','icon':'🐍'},
    {'id':'html',   'name':'HTML/CSS','icon':'🌐'},
    {'id':'js',     'name':'JavaScript','icon':'⚡'},
    {'id':'help',   'name':'Ёрдам','icon':'🆘'},
]

@app.route('/api/chat/rooms')
@login_required
def chat_rooms():
    db = get_db(); rooms=[]
    for r in ROOMS:
        last = db.execute(
            "SELECT m.text,u.name FROM messages m JOIN users u ON m.user_id=u.id "
            "WHERE m.room_id=? ORDER BY m.id DESC LIMIT 1",(r['id'],)).fetchone()
        rooms.append({**r,'last_message':dict(last) if last else None,
            'count':db.execute("SELECT COUNT(*) FROM messages WHERE room_id=?",(r['id'],)).fetchone()[0]})
    db.close(); return jsonify(rooms)

@app.route('/api/chat/<room_id>/messages')
@login_required
def chat_messages(room_id):
    limit = request.args.get('limit',50,type=int); db=get_db()
    msgs  = rows2list(db.execute("""
        SELECT m.id,m.text,m.created_at,m.user_id,u.name as user_name,u.avatar
        FROM messages m JOIN users u ON m.user_id=u.id
        WHERE m.room_id=? ORDER BY m.id DESC LIMIT ?""",(room_id,limit)).fetchall())
    db.close(); msgs.reverse(); return jsonify(msgs)

@app.route('/api/chat/<room_id>/send', methods=['POST'])
@login_required
def chat_send(room_id):
    text=(request.get_json().get('text') or '').strip()
    if not text: return jsonify({'error':'Паём холӣ аст'}),400
    if len(text)>1000: return jsonify({'error':'Паём хеле дароз аст'}),400
    db  = get_db()
    cur = db.execute("INSERT INTO messages (room_id,user_id,text) VALUES (?,?,?)",
        (room_id,session['user_id'],text))
    msg = row2dict(db.execute("""
        SELECT m.id,m.text,m.created_at,m.user_id,u.name as user_name,u.avatar
        FROM messages m JOIN users u ON m.user_id=u.id WHERE m.id=?""",(cur.lastrowid,)).fetchone())
    db.commit(); db.close(); return jsonify(msg),201


# =====================================================
# SCHEDULE API
# =====================================================
@app.route('/api/schedule')
@login_required
def get_schedule():
    db=get_db()
    items=rows2list(db.execute("SELECT * FROM schedule ORDER BY day_of_week,time").fetchall())
    db.close(); return jsonify(items)

@app.route('/api/schedule', methods=['POST'])
@admin_required
def create_schedule():
    d=request.get_json()
    if not d.get('title'): return jsonify({'error':'Унвон ҳатмӣ!'}),400
    db=get_db()
    cur=db.execute("INSERT INTO schedule (title,type,day_of_week,time,duration,repeat) VALUES (?,?,?,?,?,?)",
        (d['title'],d.get('type','lesson'),d.get('day_of_week',1),
         d.get('time','09:00'),d.get('duration',60),d.get('repeat','weekly')))
    db.commit()
    item=row2dict(db.execute("SELECT * FROM schedule WHERE id=?",(cur.lastrowid,)).fetchone())
    db.close(); return jsonify(item),201

@app.route('/api/schedule/<int:sid>', methods=['DELETE'])
@admin_required
def delete_schedule(sid):
    db=get_db(); db.execute("DELETE FROM schedule WHERE id=?",(sid,))
    db.commit(); db.close(); return jsonify({'success':True})


# =====================================================
# NOTIFICATIONS API
# =====================================================
@app.route('/api/notifications')
@login_required
def get_notifications():
    uid=session['user_id']; db=get_db()
    ns=rows2list(db.execute(
        "SELECT * FROM notifications WHERE user_id=? OR user_id IS NULL ORDER BY id DESC LIMIT 30",
        (uid,)).fetchall())
    db.close(); return jsonify(ns)

@app.route('/api/notifications/read', methods=['POST'])
@login_required
def mark_read():
    uid=session['user_id']; db=get_db()
    db.execute("UPDATE notifications SET is_read=1 WHERE user_id=?",(uid,))
    db.commit(); db.close(); return jsonify({'success':True})

@app.route('/api/notifications/broadcast', methods=['POST'])
@admin_required
def broadcast():
    d=request.get_json(); msg=d.get('message',''); icon=d.get('icon','🔔')
    if not msg: return jsonify({'error':'Паём холӣ аст'}),400
    db=get_db()
    sts=db.execute("SELECT id FROM users WHERE role='student'").fetchall()
    for s in sts:
        db.execute("INSERT INTO notifications (user_id,message,icon) VALUES (?,?,?)",(s[0],msg,icon))
    db.commit(); db.close()
    return jsonify({'success':True,'sent_to':len(sts)})


# =====================================================
# RUN
# =====================================================
if __name__ == '__main__':
    init_db()
    print("="*50)
    print("  ПлатформаТЈ — http://localhost:5000")
    print("  Админ:   admin / admin123")
    print("  Хонанда: student1 / pass123")
    print("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)

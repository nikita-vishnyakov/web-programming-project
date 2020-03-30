import os
import csv
import random
from functools import wraps
import pymysql
import hashlib, uuid
from Models import Model

from flask import Flask, request, render_template, session, redirect, url_for
# from flask_sqlalchemy import *
import pymysql
import _datetime as datetime
import keys
# pymysql.install_as_MySQLdb()

app = Flask(__name__)
con = pymysql.connect(keys.pymysql_host, keys.pymysql_user, keys.pymysql_password, keys.pymysql_database)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Пример строки подключения
# db.bind(provider='mysql', host='<ваше_имя>.mysql.pythonanywhere-services.com', user='<ваше_имя>', passwd='<пароль БД>', db='default')


# Model.db.bind(provider=keys.provider, host=keys.host, user=keys.user, passwd=keys.passwd, db=keys.db)

def create_db_structure():
    Model.db.generate_mapping(create_tables=True)


@app.route('/',  methods=['GET', 'POST'])
def page_index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        if check_user(request.form.get('username'), request.form.get('password')):
            next_url = request.args.get('next')
        else:
            err_mess=1
            return render_template('index.html', err_mess=err_mess)
        if next_url:
            if not request.form['username']:
                return redirect(url_for('page_index', next=next_url))
            return redirect(next_url)
        return redirect(url_for('page_home'))

def check_user(login, password):
    cursor = con.cursor()
    hash_pass = hashlib.md5(password.encode())
    sql = "select * from patients where login=%s and password=%s"
    cursor.execute(sql, (login, hash_pass.hexdigest()))

    row = cursor.fetchone()
    if row is None:
        return False
    else:
        personal_data = {'patients_id': row[0], 'lastname': row[1], 'firstname': row[2], 'patronimic': row[3], 'gender': row[4], 'birthdate': row[5], 'login': row[6]}
        session['personal_data'] = personal_data
        return True


@app.route('/logout')
def logout():
    session.pop('personal_data', None)
    return redirect(url_for('page_index'))


@app.route('/home', methods=['GET', 'POST'])
def page_home():
    week_day = ""
    date = datetime.datetime.today().strftime("%d.%m.%Y")
    day_num = datetime.datetime.today().isoweekday()
    if day_num == 1:
        week_day = "Понедельник"
    elif day_num == 2:
        week_day = "Вторник"
    elif day_num == 3:
        week_day = "Среда"
    elif day_num == 4:
        week_day = "Четверг"
    elif day_num == 5:
        week_day = "Пятница"
    elif day_num == 6:
        week_day = "Суббота"
    elif day_num == 7:
        week_day = "Воскресенье"
    else:
        week_day = "Самый прекрасный день недели"
    return render_template('home.html', week_day=str(week_day), date=date)


@app.route('/about')
def page_about():
    return render_template('about.html')


def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['personal_data']['patients_id']:
            return redirect(url_for('page_index',
                                      next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/doctors')
def page_doctors():
    cursor = con.cursor()
    sql = "SELECT * FROM doctors;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return render_template('doctors.html', data=rows)


@app.route('/add_doctors', methods=['GET', 'POST'])
def add_doctors():
    cursor = con.cursor()
    cursor.execute("SELECT * FROM qualifications;")
    req = cursor.fetchall()
    if request.method == 'GET':
        return render_template('add_doctors.html', qualifications=req)
    if request.method == 'POST':
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        patronimic = request.form.get('patronimic')
        gender = request.form.get('gender')
        birthday = request.form.get('birthdate')
        qualification = ''
        qualification = request.form.get('qualification')
        #print(("'{0}', '{1}', '{2}', '{3}', '{4}')".format(lastname, firstname, patronimic, gender, birthday)))
        sql = "INSERT INTO doctors (lastname, firstname, patronimic, gender, birthday, qualification) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}');"\
            .format(lastname, firstname, patronimic, gender, birthday, qualification)
        cursor.execute(sql)
        con.commit()
        return render_template('add_doctors.html', qualifications=req)


@app.route('/patients')
@requires_login
def page_patients():
    cursor = con.cursor()
    cursor.execute("SELECT * FROM patients;")
    data = cursor.fetchall()
    quant_h = [0, 0, 0]  # Element 0 - quantity men, 1 - qunatity womens, 2 -both.
    cursor.execute(
        "select * from((select count(*) as count_men from patients where gender = 'М') as t1, (select count(*) as count_women from patients where gender = 'Ж') as t2);")
    rows = cursor.fetchall()
    quant_h[0] = rows[0][0]
    quant_h[1] = rows[0][1]
    quant_h[2] = quant_h[0] + quant_h[1]
    return render_template('patients.html', data=data, quant_h=quant_h, res=rows)


@app.route('/upload', methods=['GET', 'POST'])
def page_upload():
    if request.method == 'POST':
        f = request.files['usr_file']
        path = os.path.join(os.getcwd(), 'data', f.filename)
        f.save(path)
        return page_index()
    return render_template('upload.html')


@app.route('/add_patients', methods=['GET', 'POST'])
def add_patients():
    cursor = con.cursor()
    mess = {'success': [], 'error': []}
    if request.method == 'GET':
        return render_template('add_patients.html', mess=mess)
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        re_password = request.form.get('re-password')
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        patronimic = request.form.get('patronimic')
        gender = request.form.get('gender')
        if gender == "male":
            gender = "М"
        if gender == "female":
            gender = "Ж"
        birthdate = request.form.get('birthdate')
        if len(password) == 0:
            mess['error'].append("Значение пароля отсутствует.")
            return render_template('add_patients.html', mess=mess)
        if password != re_password:
            mess['error'].append("Пароли не совпадают.")
            return render_template('add_patients.html', mess=mess)
        if not_exist_user(login):
            hash_pass = hashlib.md5(password.encode()).hexdigest()
            sql = "INSERT INTO patients (login, password, lastname, firstname, patronimic, gender, birthday) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');"\
                .format(login, hash_pass, lastname, firstname, patronimic, gender, birthdate)
            #print(sql)
            cursor.execute(sql)
            mess['success'].append("Аккаунт был успешно зарегистрирован.")
            con.commit()
        else:
            mess['error'].append("Пользователь с таким логином уже существует.")
            return render_template('add_patients.html', mess=mess)
        return render_template('add_patients.html', mess=mess)


def not_exist_user(login):
    cursor = con.cursor()
    sql = "SELECT COUNT(*) FROM patients WHERE login=%s"
    cursor.execute(sql, login)
    row = cursor.fetchone()
    if row[0] == 0:
        return True
    else:
        return False


@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    cursor = con.cursor()
    if not 'personal_data' in session:
        err_mess = 1
        next_url = request.args.get('next')
        return redirect(url_for('page_index', next=next_url))
    sql = "SELECT doctors_id, lastname, firstname, patronimic, gender, qualifications.title as qualification FROM doctors INNER JOIN qualifications on doctors.qualification = qualifications.id;"
    cursor.execute(sql)
    row = cursor.fetchall()
    if request.method == "POST":
        doctors_id = request.form.get('doctor')
        date_time = request.form.get('datetime')
        sql = "INSERT INTO consultation (patients_id, doctors_id, consultation_date) VALUES ('{0}', '{1}', '{2}')".format(session['personal_data']['patients_id'], doctors_id, date_time)
        cursor.execute(sql)
        con.commit()
        return render_template('add_record.html', list_doctors=row)
    return render_template('add_record.html', list_doctors=row)


@app.route('/view_records')
def view_records():
    cursor = con.cursor()
    sql = "SELECT p.lastname, p.firstname, p.patronimic, d.lastname, d.firstname, d.patronimic, consultation.consultation_date, q.title FROM consultation" \
          " INNER JOIN patients p ON consultation.patients_id = p.patients_id INNER JOIN doctors d ON consultation.doctors_id = d.doctors_id INNER JOIN qualifications q ON d.qualification=q.id;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    return render_template('view_records.html', list_records=rows)

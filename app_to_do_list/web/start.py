import calendar
from datetime import datetime, timedelta

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from models import User, Events
from settings import app, manager, db
from tasks import send_async_email
from werkzeug.security import generate_password_hash, check_password_hash


dt_start = "2000-01-01"
dt_end = "2050-01-01"
user = ''


@manager.user_loader
def load_user(user_id):
    global user

    user = User.query.get(user_id)

    return user


@app.route('/login/', methods=['GET', 'POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(username=login).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            return redirect(url_for('Index'))
        else:
            flash('Login or password is not correct')

    else:
        flash('Pleas fill login and password fields')

    return render_template('login.html')


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Pleas, fill all fields')
        elif password != password2:
            flash('Passworda are not equal')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(username=login, email=email, password_hash=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/')
@login_required
def Index():
    global dt_start
    global dt_end
    global user
    dt_start = "2000-01-01"
    dt_end = "2050-01-01"

    all_data = Events.query.filter(Events.user_email == user.email).order_by(Events.date.asc(), Events.time.asc()).all()

    return render_template('index.html', events=all_data)


@app.route('/insert', methods = ['POST'])
@login_required
def insert():
    global user

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        title = request.form['title']
        event_content = request.form['event_content']

        data_event = Events(date, time, title, event_content)
        data_event.author = user
        db.session.add(data_event)
        db.session.commit()

        email_data = {
            'subject': title,
            'to': user.email,
            'body': event_content
        }

        date_time = date + " " + time
        datetime_object = datetime.strptime(date_time, '%Y-%m-%d %H:%M') - timedelta(hours=4)
        eta_date = datetime.utcfromtimestamp(datetime_object.timestamp()).strftime('%Y-%m-%d %H:%M:%S')
        send_async_email.apply_async(args=[email_data], eta=eta_date)

        flash('New event inserted successfully')

        return redirect(url_for('Index'))


@app.route('/update', methods= ['GET', 'POST'])
@login_required
def update():

    if request.method == 'POST':
        data = Events.query.get(request.form.get('id'))
        data.date = request.form['date']
        data.time = request.form['time']
        data.title = request.form['title']
        data.event_content = request.form['event_content']

        db.session.commit()
        flash('Event updated successfully')

        return redirect(url_for('Index'))


@app.route('/delete/<id>', methods = ['GET', 'POST'])
@login_required
def delete(id):

    data = Events.query.get(id)
    db.session.delete(data)
    db.session.commit()

    flash('Event deleted successfully')

    return redirect(url_for('Index'))


@app.route('/filter/<int:param>', methods = ['GET', 'POST'])
@login_required
def filter(param):
    global dt_start
    global dt_end
    global user

    if param == 1:
        data = Events.query.filter(Events.date == datetime.today().strftime('%Y-%m-%d'), Events.user_email == user.email).order_by(Events.date.asc(),
                                                                                                  Events.time.asc()).all()
        dt_start = datetime.today().strftime('%Y-%m-%d')
        dt_end = datetime.today().strftime('%Y-%m-%d')

        return render_template('index.html', events=data)

    elif param == 2:
        data_now = datetime.now()
        num_week = calendar.weekday(data_now.year, data_now.month, data_now.day)
        date_start = data_now - timedelta(0 + num_week)
        date_end = data_now + timedelta(6 - num_week)
        dt_start = date_start.strftime('%Y-%m-%d')
        dt_end = date_end.strftime('%Y-%m-%d')

        data = Events.query.filter(Events.date >= date_start.strftime('%Y-%m-%d'),
                                   Events.date <= date_end.strftime('%Y-%m-%d'), Events.user_email == user.email).order_by(Events.date.asc(),
                                                                                          Events.time.asc()).all()

        return render_template('index.html', events=data)

    else:
        today = datetime.today()
        last_date = calendar.monthrange(today.year, today.month)[1]
        date_str = today.strftime('%Y-%m-%d')
        date_start = date_str[:8] + "01"
        date_end = date_str[:8] + str(last_date)
        dt_start = date_start
        dt_end = date_end

        data = Events.query.filter(Events.date >= date_start, Events.date <= date_end, Events.user_email == user.email).order_by(Events.date.asc(), Events.time.asc()).all()

        return render_template('index.html', events=data)


@app.route('/filter_date', methods = ['GET', 'POST'])
@login_required
def filter_date():
    global dt_start
    global dt_end
    global user
    if request.method == 'POST':
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')

        dt_start = date_start
        dt_end = date_end

        data = Events.query.filter(Events.date >= date_start, Events.date <= date_end, Events.user_email == user.email).order_by(Events.date.asc(), Events.time.asc()).all()

        return render_template('index.html', events=data)


@app.route('/filter_title', methods = ['GET', 'POST'])
@login_required
def filter_title():
    global dt_start
    global dt_end
    global user
    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            data = Events.query.filter(Events.date >= dt_start, Events.date <= dt_end, Events.title == title, Events.user_email == user.email).order_by(Events.date.asc(), Events.time.asc()).all()

            return render_template('index.html', events=data)
        return redirect(url_for('Index'))


@app.route('/events/<int:id>', methods = ['GET', 'POST'])
@login_required
def events(id):

    data = Events.query.filter(Events.id == id, Events.user_email == user.email)

    return render_template('index.html', events=data)


if __name__== "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)

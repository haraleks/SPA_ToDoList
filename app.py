import calendar
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://test1:Test1_2020@localhost/crud"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'haraleks88@gmail.com'  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = 'haraleks88@gmail.com'  # и здесь
app.config['MAIL_PASSWORD'] = 'password'  # введите пароль

db = SQLAlchemy(app)
db.create_all()
mail = Mail(app)


dt_start = "2000-01-01"
dt_end = "2050-01-01"


class Data(db.Model):
    __tablename__ = 'data_events'
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    title = db.Column(db.Text(255), nullable=False)
    event_content = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, date, time, title, event_content):
        self.date = date
        self.time = time
        self.title = title
        self.event_content = event_content


@app.route('/')
def Index():
    global dt_start
    global dt_end
    dt_start = "2000-01-01"
    dt_end = "2050-01-01"

    all_data = Data.query.order_by(Data.date.asc(),Data.time.asc()).all()
    # data = Data.query.filter_by(date=datetime.today().strftime('%Y-%m-%d')).all()

    return render_template('index.html', events=all_data)


@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        title = request.form['title']
        event_content = request.form['event_content']

        data_event = Data(date, time, title, event_content)
        db.session.add(data_event)
        db.session.commit()

        flash('New event inserted successfully')

        return redirect(url_for('Index'))


@app.route('/update', methods= ['GET', 'POST'])
def update():

    if request.method == 'POST':
        data = Data.query.get(request.form.get('id'))
        data.date = request.form['date']
        data.time = request.form['time']
        data.title = request.form['title']
        data.event_content = request.form['event_content']

        db.session.commit()
        flash('Event updated successfully')

        return redirect(url_for('Index'))


@app.route('/delete/<id>', methods = ['GET', 'POST'])
def delete(id):

    data = Data.query.get(id)
    db.session.delete(data)
    db.session.commit()

    flash('Event deleted successfully')

    return redirect(url_for('Index'))


@app.route('/filter/<int:param>', methods = ['GET', 'POST'])
def filter(param):
    global dt_start
    global dt_end

    if param == 1:
        data = Data.query.filter(Data.date == datetime.today().strftime('%Y-%m-%d')).order_by(Data.date.asc(),
                                                                                              Data.time.asc()).all()
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

        data = Data.query.filter(Data.date >= date_start.strftime('%Y-%m-%d'),
                                 Data.date <= date_end.strftime('%Y-%m-%d')).order_by(Data.date.asc(),
                                                                                      Data.time.asc()).all()

        return render_template('index.html', events=data)

    else:
        today = datetime.today()
        last_date = calendar.monthrange(today.year, today.month)[1]
        date_str = today.strftime('%Y-%m-%d')
        date_start = date_str[:8] + "01"
        date_end = date_str[:8] + str(last_date)
        dt_start = date_start
        dt_end = date_end

        data = Data.query.filter(Data.date >= date_start, Data.date <= date_end).order_by(Data.date.asc(),Data.time.asc()).all()

        return render_template('index.html', events=data)


@app.route('/filter_date', methods = ['GET', 'POST'])
def filter_date():
    global dt_start
    global dt_end
    if request.method == 'POST':
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')

        dt_start = date_start
        dt_end = date_end


        data = Data.query.filter(Data.date >= date_start, Data.date <= date_end).order_by(Data.date.asc(),Data.time.asc()).all()

        return render_template('index.html', events=data)


@app.route('/filter_title', methods = ['GET', 'POST'])
def filter_title():
    global dt_start
    global dt_end
    if request.method == 'POST':
        print(dt_start)
        print(dt_end)
        title = request.form.get('title')
        if title:
            data = Data.query.filter(Data.date >= dt_start, Data.date <= dt_end, Data.title == title).order_by(Data.date.asc(),Data.time.asc()).all()

            return render_template('index.html', events=data)
        return redirect(url_for('Index'))


@app.route('/events/<int:id>', methods = ['GET', 'POST'])
def events(id):

    data = Data.query.filter(Data.id == id)

    return render_template('index.html', events=data)


if __name__== "__main__":
    app.run(debug=True)
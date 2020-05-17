from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://test1:Test1_2020@localhost/crud"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.create_all()

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
    all_data = Data.query.all()

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

if __name__== "__main__":
    app.run(debug=True)
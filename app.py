import csv
import pathlib
import sqlite3

import requests
from faker import Faker
from flask import Flask, render_template, request, redirect

fake = Faker('ru_RU')
app = Flask(__name__)
DB_PATH = pathlib.Path('db', 'db.sqlite')


class Connection:
    def __init__(self):
        self._connection: sqlite3.Connection | None = None

    def __enter__(self):
        self._connection = sqlite3.connect(DB_PATH)
        self._connection.row_factory = sqlite3.Row
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/requirements')
def requirements():
    file_name = 'requirements.txt'
    try:
        with open(file_name) as f:
            text = f.read()
    except FileNotFoundError:
        text = 'Не удалось прочитать файл.'
    return render_template("requirements.html", text=text, file_name=file_name)


@app.route('/generate-users', methods=['POST', 'GET'])
def generate_users():
    if request.method == 'POST':
        quantity = request.form['quantity']
        users = generator(int(quantity))
    else:
        users = generator()
    return render_template("generate-users.html", users=users)


@app.route('/space')
def space():
    people = get_space('http://api.open-notify.org/astros.json')

    return render_template("space.html", people=people)


@app.route('/mean')
def mean():
    file_name = 'people_data.csv'
    average = get_average(file_name)
    return render_template("mean.html", average=average)


@app.route('/phones/read')
def phones_read():
    with Connection() as connection:
        records = connection.execute('SELECT * FROM phones').fetchall()
    return render_template('phones.html', records=records)


@app.route('/phones/create', methods=['POST', 'GET'])
def phones_create():
    if request.method == 'POST':
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        with Connection() as connection:
            with connection:
                connection.execute('INSERT INTO phones (contactName, phoneValue) VALUES (:name, :phone)',
                                   (contact_name, contact_phone))
        return redirect('/phones/read')
    else:
        return render_template("create.html")


@app.route('/phones/delete/<int:phoneID>')
def phones_delete(phoneID):
    with Connection() as connection:
        with connection:
            connection.execute('DELETE FROM phones WHERE (phoneID=:phoneID)', {'phoneID': phoneID})
    return redirect('/phones/read')


@app.route('/phones/update/<int:phoneID>', methods=['POST', 'GET'])
def phones_update(phoneID):
    if request.method == 'POST':
        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']
        print(contact_name)
        print(phoneID)
        with Connection() as connection:
            with connection:
                connection.execute(
                    'UPDATE phones '
                    'SET contactName=:contact_name, phoneValue=:contact_phone '
                    'WHERE (phoneID=:phoneID)',
                    {"contact_name": contact_name, "contact_phone": contact_phone, "phoneID": phoneID}
                )
        return redirect('/phones/read')
    else:
        with Connection() as connection:
            record = connection.execute('SELECT * FROM phones WHERE (phoneID=:phoneID)',
                                        {'phoneID': phoneID}).fetchall()
        return render_template("update.html", record=record)


def get_space(url: str) -> tuple:
    response = requests.get(url)
    number_of_people = response.json()['number']
    names = [i['name'] for i in response.json()['people']]
    return names, number_of_people


def generator(quantity: int = 100) -> list:
    return [f'{fake.first_name()} {fake.email()}' for _ in range(quantity)]


def get_average(file_name: str) -> tuple:
    all_weights = []
    all_heights = []
    try:
        with open(file_name) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                all_heights.append(float(row[' "Height(Inches)"']))
                all_weights.append(float(row[' "Weight(Pounds)"']))
    except FileNotFoundError:
        return 'Не удалось прочитать файл.'
    average_weights = round((sum(all_weights) / len(all_weights)) / 2.205, 2)
    average_heights = round((sum(all_heights) / len(all_heights)) * 2.54, 2)
    return average_heights, average_weights


if __name__ == '__main__':
    app.run()

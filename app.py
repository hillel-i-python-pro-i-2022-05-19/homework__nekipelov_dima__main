import csv

import requests
from faker import Faker
from flask import Flask, render_template, request

fake = Faker('ru_RU')
app = Flask(__name__)


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

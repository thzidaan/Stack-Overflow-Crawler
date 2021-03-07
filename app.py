from flask import Flask, json, render_template, request, redirect
import requests
import json
import time

app = Flask(__name__)

# (1615523017 - 1614918217) (i.e March 11 - March 4 ==> 1 week)
seven_days_time = 604800
current_Time = int(time.time())  # Gets Current Time
# Sets from date for the API request
week_earlier_time = str(current_Time - seven_days_time)

# post_id == question_id --> Remember
# Use Search API

post_endpoint = 'https://api.stackexchange.com/2.2/posts'  # Will be used for comments
question_endpoint = 'https://api.stackexchange.com/2.2/questions'


comment_endpoint = "{ids}/comments?pagesize=100&order=desc&sort=creation&site=stackoverflow"
most_voted_endpoint = '?pagesize=10&fromdate=' + \
    week_earlier_time + '&order=asc&sort=votes&site=stackoverflow'
most_recent_endpoint = '?pagesize=10&order=asc&sort=creation&site=stackoverflow&tagged='


questionCollection = {}


@app.route('/search', methods=['POST'])
def search():

    tag_selected = request.form["tag"]

    most_voted_posts = question_endpoint + most_voted_endpoint + tag_selected
    most_recent_posts = question_endpoint + most_recent_endpoint + tag_selected

    most_voted_request = requests.get(most_voted_posts)
    most_recent_request = requests.get(most_recent_posts)

    votes_data = dict(json.loads(most_voted_request.content))
    recent_data = dict(json.loads(most_recent_request.content))
    total_questions = dict(votes_data, **recent_data)

    total_question_items = total_questions['items']

    for item in total_question_items:
        questionCollection[item['question_id']] = {  # question_id will help us find corresponding comments
            'title': item['title'],
            'votes': item['score'],
            'creation_date': item['creation_date']
        }

    return render_template('search.html', data=questionCollection)


@ app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

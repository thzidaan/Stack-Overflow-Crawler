from flask import Flask, render_template, request
import requests
import time
from operator import itemgetter
from datetime import datetime
from flaskext.markdown import Markdown


app = Flask(__name__)
Markdown(app)

# (1615523017 - 1614918217) (i.e March 11 - March 4 ==> 1 week)
seven_days_time = 604800
current_Time = int(time.time())  # Gets Current Time
# Sets from date for the API request
week_earlier_time = str(current_Time - seven_days_time)

# post_id == question_id --> Remember
# Use Search API
search_base_endpoint = 'https://api.stackexchange.com/2.2/search'


most_voted_endpoint = '?pagesize=10&fromdate=' + week_earlier_time + \
    '&order=desc&sort=votes&site=stackoverflow&filter=!0VdjgcAdM-31Pt4LHr5ojF5Bm&tagged='
most_recent_endpoint = '?pagesize=10&fromdate=' + week_earlier_time + \
    '&order=desc&sort=creation&site=stackoverflow&filter=!0VdjgcAdM-31Pt4LHr5ojF5Bm&tagged='


def time_converter(UNIX_Time):  # Helps convert the time got from the API Call
    given_time = int(UNIX_Time)

    readable_date = datetime.utcfromtimestamp(
        given_time).strftime('%Y-%m-%d %H:%M:%S')

    return readable_date


@app.route('/search', methods=['POST'])
def search():

    start_time = time.perf_counter()

    tag_selected = request.form["tag"]  # Gets Tag from input

    comments_collection = []  # Arrays to collect information for the response
    answers_collection = []
    questions_collection = []
    question_comment_collection = []

    most_voted_search = search_base_endpoint + most_voted_endpoint + tag_selected
    most_recent_search = search_base_endpoint + most_recent_endpoint + tag_selected

    most_voted_request = requests.get(most_voted_search).json()
    most_recent_request = requests.get(most_recent_search).json()

    all_request_data = [
        most_voted_request,
        most_recent_request
    ]

    for request_item in all_request_data:

        if request_item.get('items') is not None:

            all_data = request_item.get('items')

            for item_list in range(len(request_item['items'])):

                if ((request_item.get('items')[item_list]).get('answers')) is not None:

                    # We get all the answers for the current question
                    all_answers_data = (
                        (request_item.get('items')[item_list]).get('answers'))
                    for answer_list in range(len(all_answers_data)):

                        answer_item = all_answers_data[answer_list]

                        # If answer also have comments
                        if (((
                                (request_item.get('items')[item_list]).get('answers'))[answer_list]).get('comments')) is not None:

                            answer_item_comments = (((
                                (request_item.get('items')[item_list]).get('answers'))[answer_list]).get('comments'))
                            for answer_comment_list in range(len(answer_item_comments)):
                                # Taking each comment from answers
                                answer_comment_item = answer_item_comments[answer_comment_list]
                                new_comment = {
                                    'creation_date': time_converter(answer_comment_item['creation_date']),
                                    'score': answer_comment_item['score'],
                                    'body': answer_comment_item['body_markdown']
                                }
                                comments_collection.append(new_comment)
                            comments_collection = sorted(
                                comments_collection, key=itemgetter('score'), reverse=True)  # Answer_comments get sorted by Score

                        new_answer = {
                            'creation_date': time_converter(answer_item['creation_date']),
                            'score': answer_item['score'],
                            'body': answer_item['body_markdown'],
                            'comments': comments_collection
                        }
                        answers_collection.append(new_answer)
                        comments_collection = []  # Comment array has been cleared for the next set of answers
                    answers_collection = sorted(
                        answers_collection, key=itemgetter('score'), reverse=True)  # Answers gets sorted by votes
                # If the question has comments
                if ((request_item.get('items')[item_list]).get('comments')) is not None:
                    all_question_comment_data = (
                        (request_item.get('items')[item_list]).get('comments'))
                    for question_comment_list in range(len(all_question_comment_data)):
                        question_comment_item = all_question_comment_data[question_comment_list]

                        new_question_comment_item = {
                            'creation_date': time_converter(question_comment_item['creation_date']),
                            'score': question_comment_item['score'],
                            'body': question_comment_item['body_markdown']
                        }
                        question_comment_collection.append(
                            new_question_comment_item)

                    question_comment_collection = sorted(
                        question_comment_collection, key=itemgetter('score'), reverse=True)  # Question comments get sorted by votes

                question_item = (request_item.get('items')[item_list])
                new_question = {
                    'title': question_item['title'],
                    'score': question_item['score'],
                    'creation_date': time_converter(question_item['creation_date']),
                    'body': question_item['body_markdown'],
                    'comments': question_comment_collection,
                    'answers': answers_collection
                }
                questions_collection.append(new_question)
                answers_collection = []  # answer collection cleared for next question
                # Question comment collection freed for next question
                question_comment_collection = []

    end_time = time.perf_counter()
    performance_time = end_time - start_time

    sorted_question_collection = sorted(
        questions_collection, key=itemgetter('creation_date'), reverse=True)

    return render_template('search.html', data=sorted_question_collection, response_time=performance_time, tagged=tag_selected)


@ app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()

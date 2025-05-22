from flask import Flask, render_template, Response, jsonify, session, request, redirect
import that_many_questions_in_how_many_seconds as quiz
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'jimbo76'

MAX_MINUTE_DURATION = 2




@app.route('/') 
def home():
    if 'score' not in session:
        session['score'] = 0
    if 'high_score' not in session:
        session['high_score'] = 0

    session['difficulty'] = 5
        
    _, question, answer, points = quiz.generate_question(0, session['difficulty'], 0)
    session['question'] = question
    session['answer'] = answer  # Store correct answer in session for validation
    session['points'] = points

    if 'expiration_time' not in app.config:
        get_expiration()

    remaining_time = app.config['expiration_time'] - datetime.now()
    time_remaining = remaining_time.total_seconds() > 0

    return render_template('index.html', question=question, time_remaining=time_remaining)



def safe_eval(expr):
    allowed = set("0123456789+-*/(). ")
    if all(char in allowed for char in expr):
        return eval(expr)


@app.route('/submit', methods=['POST'])
def submitted():
    # Get and process user answer
    user_answer = request.form['user_answer']
    float_user_answer = safe_eval(user_answer)

    correct_answer = session.get('answer')

    if correct_answer is not None and float_user_answer == correct_answer:
        session['score'] += max(session['points'] * 2 - 1, 1) # Scaling higher points for more difficult
    session['user_previous_answer'] = float_user_answer
    session['previous_answer'] = correct_answer
    print(f'session["user_previous_answer"] = {float_user_answer}')
    print(f'session["previous_answer"] = {correct_answer}')
    if "question" in session:
        print(f'session["question"] = {session["question"]}')

    return redirect('/')




@app.route('/restart', methods=['POST'])
def restart():
    session['score'] = 0
    get_expiration()
    return redirect('/')




def get_expiration():
    app.config['expiration_time'] = datetime.now() + timedelta(minutes=MAX_MINUTE_DURATION) + timedelta(seconds = 2)

def get_remaining_time_in_seconds():
    if 'expiration_time' not in app.config:
        get_expiration()
    remaining_time = app.config['expiration_time'] - datetime.now()
    remaining_time_in_seconds = remaining_time.total_seconds()
    return remaining_time_in_seconds





@app.route('/remaining_time')
def remaining_time():
    remaining_time_in_seconds = get_remaining_time_in_seconds()
    if remaining_time_in_seconds <= 0:
        # Times up!
        if session['high_score'] > session['score']:
            # User didnt beat score
            session['user_won'] = False
        else:
            # User beat score
            session['user_won'] = True

            # Update high score
            session['high_score'] = session['score']
        
    return jsonify({'remaining_time_in_seconds': remaining_time_in_seconds})

if __name__ == "__main__":
    app.run(debug=True)
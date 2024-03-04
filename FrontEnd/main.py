from flask import Flask,flash, render_template, jsonify, send_from_directory, request
from flask_toastr import Toastr
import requests
import json

app = Flask(__name__)
toastr = Toastr(app)

@app.route('/')
def home():
    return render_template('index.html')

# Route to serve the favicon.ico file
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'static/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/test')
def test():
    api_url = 'http://localhost:32773/'
    response = requests.get(api_url)

    if response.status_code == 200:
        json_data = response.json()
        return render_template('test.html', data=json_data)
    else:
        return jsonify({'error': 'Failed to fetch data from API'}), response.status_code

@app.route('/', methods=['POST'])
def upload_file():
    #Check if the POST request has the file
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['pdf_file']

    #Check if file is present
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Send the file to the FastAPI endpoint
    api_url = 'http://localhost:32773/upload/'
    files = {'file': (file.filename, file.stream, file.mimetype)}
    response = requests.post(api_url, files=files)

    if(response.status_code == 200):
        flash(response.text, "success")
        return render_template('index.html')
    else:
        flash(response.text, "error")
        return render_template('index.html')

@app.route('/qa', methods=['POST'])
def submit():
    try:
        # Extract the question data from the request body
        question_data = request.json
        # Access the value of the "question" key from the JSON data
        text_input = question_data.get('question')
        response = requests.post('http://127.0.0.1:8000/getsql/', json={'query': text_input})

        data = response.json()
        # Access the value of the "question" and "answer" keys from the JSON data
        question = data.get('question')
        answer = data.get('answer')

        # Return the question and answer in the response
        response_data = {
            'question': question,
            'answer': answer
        }
        return jsonify(response_data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.secret_key = 'super secret key'#NEEDS TO CHANGE!!!
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
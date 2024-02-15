from flask import Flask, render_template
from urllib.request import urlopen 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    with urlopen('http://localhost:323768') as r:
        text = r.read()
    return render_template('test.html', value  = text)

if __name__ == '__main__':
    app.run(debug=True)
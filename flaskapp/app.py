from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rekon')
def rekon():
    return render_template('webcam2.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
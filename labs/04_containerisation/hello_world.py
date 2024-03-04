from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    # HTML code to display a specific message. You can try something else :-)
    return '<h1>Hello World! Happy learning Machine Learning Systems Designs!</h1>'

if __name__ == '__main__':
    # Set the server to run on port 8080
    app.run(debug=True, host='localhost', port=8080)

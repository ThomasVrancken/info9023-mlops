from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello World! How are you ?'

@app.route('/hello/<username>')
def show_user_profile(username):
    return 'Hello %s!' % username

if __name__ == '__main__':
   app.debug = True
   #app.run()
   app.run(debug = True)
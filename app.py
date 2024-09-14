from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key to use sessions
socketio = SocketIO(app)

from backend.matcher import Buyer, Seller, Matcher
matcher = Matcher()
transactions = []

@app.route('/')
def login():
  if 'name' in session:
    return redirect(url_for('main_page'))

  # Otherwise, prompt for name and ID
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
  # Get name and ID from form
  session['id'] = request.form['id']
  session['name'] = request.form['name']

  # Redirect to main page
  return redirect(url_for('main_page'))

@app.route('/main')
def main_page():
  # Ensure user is logged in
  if 'name' not in session:
    return redirect(url_for('login'))
  return render_template('index.html', 
                         log=matcher.log(),
                         min_seller=matcher.get_min_seller(),
                         max_buyer=matcher.get_max_buyer(),
                         user_name=session['name'])

@app.route('/submit', methods=['POST'])
def submit_transaction():
  # Ensure user is logged in
  if 'name' not in session:
    return redirect(url_for('login'))

  # Get form data
  name = session['name']
  id = session['id']
  role = request.form['role']
  price = request.form['price']
  payment = request.form['payment']
  contact_info = request.form['contactInfo']

  time = datetime.now()
  
  if role == "buyer": 
    transaction = Buyer(
      name=name,
      id=id,
      payment=payment,
      time=time,
      max_price = float(price),
    )
    matcher.add_buyer(transaction)
  elif role == "seller":
    transaction = Seller(
      name=name,
      id=id,
      payment=payment,
      time=time,
      min_price = float(price),
    )
    matcher.add_seller(transaction)
  else:
    raise RuntimeError("Unrecognized Role")

  return redirect(url_for('main_page'))

@app.route("/buy_min", methods=["POST"])
def buy_min():

  return redirect(url_for("main_page"))


@app.route("/sell_max", methods=["POST"])
def sell_max():
  pass

if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=8080, debug=True)

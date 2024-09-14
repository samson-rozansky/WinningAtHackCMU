from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key to use sessions
socketio = SocketIO(app)

from backend.matcher import Buyer, Seller, Matcher

matcher = Matcher()
current_offers = {}
pending_transactions = {}

@app.route('/')
def login():
  if 'name' in session:
    return redirect(url_for('main_page'))
  return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
  id = request.form["id"]
  session['id'] = id
  session['name'] = request.form['name']
  current_offers[id] = None 
  pending_transactions[id] = None
  return redirect(url_for('main_page'))

@app.route('/main')
def main_page():
  if 'name' not in session:
    return redirect(url_for('login'))
  id = session["id"]
  current_offer=None if current_offers.get(id) is None else current_offers[id].to_str()
  pending_transaction=None if pending_transactions.get(id) is None else pending_transactions[id].get_info()
  # print("min=", matcher.get_min_seller().min_price)
  # print("max=", matcher.get_max_buyer().max_price)
  return render_template('index.html', 
                         log=matcher.log(),
                         current_offer=current_offer,
                         pending_transaction=pending_transaction,
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

  current_offers[id] = transaction
  return redirect(url_for('main_page'))

@app.route("/cancel-offer", methods=["POST"])
def cancel_offer():
  id = session["id"]
  assert current_offers[id] is not None
  print("offer canceled")
  if isinstance(current_offers[id], Buyer):
    matcher.remove_buyer(current_offers[id])
  else:
    matcher.remove_seller(current_offers[id])
  current_offers[id] = None
  return redirect(url_for("main_page"))

@app.route("/accept-notif-proceed", methods=["POST"])
def accept_notif_proceed():
  id = session["id"]
  print("accept notif proceed")
  assert current_offers[id] is not None
  seller = current_offers[id]
  print(seller.id, pending_transactions[seller.id].id)
  matcher.process_transaction(pending_transactions[seller.id], seller, 80085) # replace me
  pending_transactions[seller] = None
  current_offers[id] = None
  return redirect(url_for("main_page"))

@app.route("/buy-min", methods=["POST"])
def buy_min():
  id = session["id"]
  name = session["name"]
  temp = Buyer(name, id, "", "", "")
  current_offers[id] = temp
  pending_transactions[matcher.get_min_seller().id] = temp
  print("buy min")
  return redirect(url_for("main_page"))


@app.route("/sell-max", methods=["POST"])
def sell_max():
  id = session["id"]
  name = session["name"]
  temp = Seller(name, id, "", "", "")
  pending_transactions[id] = matcher.get_max_buyer()
  current_offers[id] = temp
  print("sell max")
  return redirect(url_for("main_page"))

  

if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=8080, debug=True)

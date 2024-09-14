from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
from hackcmu import analyzeData

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key to use sessions
socketio = SocketIO(app)

from backend.matcher import Buyer, Seller, Matcher

matcher = Matcher()
current_offers = {}
tran_pending = {}
tran_ac = {}

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
  return redirect(url_for('main_page'))

@app.route('/get_stock_data')
def get_stock_data():
    # Return two separate lists for times and prices
    times, prices= analyzeData.get_date_time()
    return jsonify({'times': times, 'prices': prices})

@app.route('/main')
def main_page():
  if 'name' not in session:
    return redirect(url_for('login'))
  id = session["id"]
  current_offer=None if current_offers.get(id) is None else current_offers[id].to_str()
  # print("min=", matcher.get_min_seller().min_price)
  # print("max=", matcher.get_max_buyer().max_price)
  tran_pending_id = tran_pending.get(id)
  if tran_pending_id is not None:
    cur_tran = {
      "id": tran_pending_id.id,
      "name": tran_pending_id.name,
    }
  else:
    cur_tran = None
  return render_template('index.html', 
                         log=matcher.log(),
                         current_offer=current_offer,
                         tran_pending=cur_tran,
                         min_seller=matcher.get_min_seller(),
                         max_buyer=matcher.get_max_buyer(),
                         user_name=session['name'])

  # labels = [
      # 'January',
        # 'February',
        # 'March',
        # 'April',
        # 'May',
        # 'June',
  # ]
  # data = [0, 10, 15, 8, 22, 18, 25]

@app.route('/submit', methods=['POST'])
def submit_transaction():
  # Ensure user is logged in
  if 'name' not in session:
    return redirect(url_for('login'))

  # Get form data
  info = request.json;
  print(info);
  # print(info['role'])
  # print(request.values)
  # print(request.values[0])
  # print(request.values[1])
  name = session['name']
  id = session['id']
  role = info['role']
  price = info['price']
  payment = info['paymentMethods']
  contact_info = info['contact']

  time = datetime.now().replace(microsecond=0)
  
  if role == "buyer": 
    transaction = Buyer(
      name=name,
      id=id,
      payment=payment,
      time=time,
      max_price = float(price),
      contactInfo = contact_info
    )
    if matcher.get_min_seller() != None and float(price)>=matcher.get_min_seller().min_price:
        finishTransaction(transaction, matcher.get_min_seller());
    else:
        matcher.add_buyer(transaction)
  elif role == "seller":
    transaction = Seller(
      name=name,
      id=id,
      payment=payment,
      time=time,
      min_price = float(price),
      contactInfo = contact_info
    )
    if matcher.get_max_buyer()!=None and float(price)<=matcher.get_max_buyer().max_price:
        finishTransaction(matcher.get_max_buyer(), transaction);
    else:
        matcher.add_seller(transaction)
  else:
    raise RuntimeError("Unrecognized Role")

  current_offers[id] = transaction
  return redirect(url_for('main_page'))
def finishTransaction(buyer, seller):
    print(buyer, seller);

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

@app.route("/accept-proceed", methods=["POST"])
def accept_proceed():
  id = session["id"]
  print("accept proceed")
  tran_ac[id] = tran_pending[id]
  tran_ac[tran_pending[id]] = tran_pending[tran_pending[id].id]
  return redirect(url_for("finish"))

def finishTransaction(buyer: Buyer, seller: Seller):
  tran_pending[buyer.id] = seller
  tran_pending[seller.id] = buyer

# @app.route("/accept-notif-proceed", methods=["POST"])
# def accept_notif_proceed():
#   id = session["id"]
#   print("accept notif proceed")
#   assert current_offers[id] is not None
#   seller = current_offers[id]
#   print(seller.id, pending_transactions[seller.id].id)
#   matcher.process_transaction(pending_transactions[seller.id], seller, 80085) # replace me
#   pending_transactions[seller] = None
#   current_offers[id] = None
#   return redirect(url_for("main_page"))

# @app.route("/buy-min", methods=["POST"])
# def buy_min():
#   id = session["id"]
#   name = session["name"]
#   temp = Buyer(name, id, "", "", "")
#   current_offers[id] = temp
#   pending_transactions[matcher.get_min_seller().id] = temp
#   print("buy min")
#   return redirect(url_for("main_page"))
#
#
# @app.route("/sell-max", methods=["POST"])
# def sell_max():
#   id = session["id"]
#   name = session["name"]
#   temp = Seller(name, id, "", "", "")
#   pending_transactions[id] = matcher.get_max_buyer()
#   current_offers[id] = temp
#   print("sell max")
#   return redirect(url_for("main_page"))

if __name__ == '__main__':
  socketio.run(app, debug=True)

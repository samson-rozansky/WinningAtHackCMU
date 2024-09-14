from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
from hackcmu import analyzeData

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key to use sessions
socketio = SocketIO(app)

# In-memory transaction store
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

@app.route('/get_stock_data')
def get_stock_data():
    # Return two separate lists for times and prices
    times, prices= analyzeData.get_date_time()
    return jsonify({'times': times, 'prices': prices})

@app.route('/main')
def main_page():
  # Ensure user is logged in
  if 'name' not in session:
    return redirect(url_for('login'))
  # labels = [
      # 'January',
        # 'February',
        # 'March',
        # 'April',
        # 'May',
        # 'June',
  # ]
  # data = [0, 10, 15, 8, 22, 18, 25]
  return render_template('index.html', transactions=transactions, user_name=session['name'])

@app.route('/submit', methods=['POST'])
def submit_transaction():
  # Ensure user is logged in
  if 'name' not in session:
    return redirect(url_for('login'))

  # Get form data
  id = session['id']
  name = session['name']
  role = request.form['role']
  price = request.form['price']
  payment = request.form['payment']
  contact_info = request.form['contactInfo']

  print(id, name, role, payment, contact_info)

  # Add new transaction
  transaction = {
    'id': id,
    'name': name,
    'role': role,
    'price': price,
    'payment': payment,
    'contactInfo': contact_info,
    'date': datetime.now()
  }

  transactions.append(transaction)

  # Emit real-time notifications
  if role == 'buyer':
    socketio.emit('notifySeller', {'buyer': transaction, 'seller': transaction})
  elif role == 'seller':
    socketio.emit('notifyBuyer', {'buyer': transaction, 'seller': transaction})

  return redirect(url_for('main_page'))

if __name__ == '__main__':
    socketio.run(app, debug=True)

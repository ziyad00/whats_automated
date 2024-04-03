from flask import Flask, request, render_template, redirect, url_for, session, flash, session
import openpyxl
from flask_session import Session
from cachelib.file import FileSystemCache
from flask import jsonify
import time
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from PyWp.whats import PyWp  # Ensure this is your modified PyWp class
from pyzbar.pyzbar import decode
from PIL import Image
import os
app = Flask(__name__)
SESSION_TYPE = 'cachelib'
SESSION_SERIALIZATION_FORMAT = 'json'
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="sessions"),
app.config.from_object(__name__)
message_status = {}

app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Adjust the number of workers as needed
executor = ThreadPoolExecutor(max_workers=2)


def send_messages_background(contacts, message):
    pywp = PyWp()
    successful_sends = 0
    last_successful_contact = None
    global message_status
    for contact in contacts:
        # Ensure this method returns True/False based on success
        success = pywp.send_message(contact, message)
        if True:
            successful_sends += 1
            last_successful_contact = contact
            message_status['successful_sends'] = successful_sends
            message_status['last_successful_contact'] = last_successful_contact

    message_status['status'] = 'completed'
    clear_message_status()


def clear_message_status():
    global message_status
    message_status.clear()
    # Optionally, reset specific keys instead of clearing the entire dictionary
    # message_status['successful_sends'] = 0
    # message_status['last_successful_contact'] = 'None'
    # message_status['status'] = 'ready for new operation'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid Credentials. Please try again.', 'danger')
    return render_template('login.html')


@app.route("/", methods=["GET"])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('main.html')


@app.route('/fetch-message-status', methods=['GET'])
def fetch_message_status():
    return jsonify({
        'successful_sends': message_status.get('successful_sends', 0),
        'last_successful_contact': message_status.get('last_successful_contact', 'None')
    })


@app.route("/send-message", methods=["POST"])
def send_message():
    message = request.form['message']
    file = request.files['file']
    if file and message:
        contacts = extract_contacts(file)
        if contacts:
            # Run in background
            executor.submit(send_messages_background, contacts, message)
            flash(f'{len(contacts)} contacts were processed.', 'info')
        else:
            flash("No contacts found or extracted.", 'warning')
    return redirect(url_for('index'))


def decode_barcode_from_image(image_path):
    # Load the image
    image = Image.open(image_path)
    # Decode all barcodes from the image
    decoded_objects = decode(image)
    # For simplicity, return the first barcode data if available
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None


@app.route("/take-screenshot")
def take_screenshot():
    pywp = PyWp()  # You might want to maintain a single instance of this class instead
    screenshot_path = pywp.take_screenshot()
    if screenshot_path is not None:
        # Decode barcode from the screenshot
        barcode_data = decode_barcode_from_image(
            os.path.join('static', screenshot_path))
        # Check if a barcode was found
        if barcode_data:
            # Return barcode data with the response
            return jsonify({
                'screenshot_path': url_for('static', filename=screenshot_path, _external=True) + f"?{int(time.time())}",
                'barcode_data': barcode_data
            })
    else:
        return jsonify({'error': 'No barcode found in the screenshot.'})


def extract_contacts(file):
    try:
        workbook = openpyxl.load_workbook(filename=BytesIO(file.read()))
        sheet = workbook.active
        contacts = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Assuming phone numbers are in the second column
            phone_number = row[1]
            if phone_number:
                contacts.append(str(phone_number))
        return contacts
    except Exception as e:
        print(f"Failed to process file: {e}")
        return []


if __name__ == "__main__":
    app.run(debug=True)

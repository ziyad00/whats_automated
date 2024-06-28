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
from utils import *

from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)
# scheduler = BackgroundScheduler()


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
            return redirect(url_for('qr_code'))
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


@app.route('/qr-code', methods=['GET'])
def qr_code():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('qrcode.html')


@app.route("/logout", methods=["GET"])
def logout():
    try:
        logout_util()
        session['logged_in'] = False
    except Exception as e:
        flash(f"Error during logout: {e}", "danger")

    return redirect(url_for("index"))


def send_images_background(contacts, image_file):
    successful_sends = 0
    last_successful_contact = None
    global message_status

    # Save the image to a temporary file
    image_path = os.path.join('static', image_file.filename)
    image_file.save(image_path)

    for contact in contacts:
        # Send the image
        success = pywp.send_image(contact, image_path)
        if success:
            successful_sends += 1
            last_successful_contact = contact
            message_status['successful_sends'] = successful_sends
            message_status['last_successful_contact'] = last_successful_contact
            # You can add more status updates or actions here

    message_status['status'] = 'completed'
    clear_message_status()

    # Remove the temporary image file
    os.remove(image_path)


def send_messages_or_images(contacts, text_message, image_file_path, send_order, greeting="", add_greeting=False):
    for name, contact in contacts:
        final_message = text_message
        # Check if greeting is to be added and prepend it with the name
        if add_greeting and greeting:
            personalized_greeting = f"{greeting} {name},  \n\n"
            final_message = personalized_greeting + final_message

        if send_order == "text_first":
            if final_message:
                send_text_util(contact, final_message)
                # pywp.send_message(contact, final_message)
            if image_file_path:
                pass
                # pywp.send_image(contact, image_file_path)
        elif send_order == "image_first":
            if image_file_path:
                pass
                # pywp.send_image(contact, image_file_path)
            if final_message:
                pass
                # pywp.send_message(contact, final_message)


@app.route("/send-message", methods=["POST"])
def send_message():
    text_message = request.form.get('message', '')
    contacts_file = request.files.get('contacts')
    image_file = request.files.get('image')
    send_order = request.form.get('send_order', 'text_first')

    greeting_message = request.form.get('greeting_message', '')
    add_greeting = 'add_greeting' in request.form

    if not contacts_file:
        flash("No contacts file uploaded.", 'warning')
        return redirect(url_for('index'))

    contacts = extract_contacts(contacts_file)
    if not contacts:
        flash("No contacts found or extracted.", 'warning')
        return redirect(url_for('index'))

    image_file_path = None
    if image_file:
        image_file_path = os.path.join('static', image_file.filename)
        image_file.save(image_file_path)

    # Directly use send_messages_or_images to ensure sequential processing
    executor.submit(send_messages_or_images, contacts, text_message,
                    image_file_path, send_order, greeting_message, add_greeting)

    flash(
        f'Processing {len(contacts)} contacts with send order: {send_order}.', 'info')
    return redirect(url_for('index'))


def take_screenshot_periodically():
    # Your screenshot logic here
    pywp.take_screenshot()


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
    barcode_data = take_screensho_util()
    print(f"Screenshot status code: {barcode_data}")
    if barcode_data.headers['Content-Type'] == 'image/png':
        print("Screenshot taken successfully.")
        image_path = image_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'static', 'screenshot.png')
        with open(image_path, "wb") as img_file:
            img_file.write(barcode_data.content)
        print("Screenshot saved.")
        barcode_data = decode_barcode_from_image(
            image_path)
        print(f"Decoded barcode data: {barcode_data}")
        if not barcode_data:
            print("No barcode data found.")
            session['logged_in'] = True
            return jsonify({'logged_in': False})
        return jsonify({
            'screenshot_path': url_for('static', filename=barcode_data, _external=True) + f"?{int(time.time())}",
            'barcode_data': barcode_data
        })
    else:
        return jsonify(barcode_data.json())


def extract_contacts(file):
    try:
        workbook = openpyxl.load_workbook(
            filename=BytesIO(file.read()), data_only=True)
        sheet = workbook.active
        contacts = []
        for row in sheet.iter_rows(min_row=1, values_only=True):
            # Assuming names are in the first column and phone numbers in the second
            name = row[0]
            phone_number = row[1]
            if name and phone_number:
                contacts.append((name.strip(), str(phone_number).strip()))
        return contacts
    except Exception as e:
        print(f"Failed to process file: {e}")
        return []


if __name__ == "__main__":
    # Adjust the interval as needed
    # if not scheduler.running:
    #     scheduler.start()
    #     scheduler.add_job(screenshot_task, 'interval', seconds=5)
    app.run(debug=True, host='0.0.0.0')

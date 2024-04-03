import openpyxl
import pywhatkit
import datetime
from time import sleep
# Load the workbook and select the active worksheet
# Update with your file path
wb = openpyxl.load_workbook('sheet.xlsx')
sheet = wb.active

# Loop through the rows in the Excel file
# Assuming the first row is headers
for row in sheet.iter_rows(min_row=2, values_only=True):
    phone_number = row[1]  # Assuming the phone numbers are in the first column
    if (phone_number is None):
        continue
    message = "Hey"  # Your message
    print(row)
    try:
        # Send the message
        pywhatkit.sendwhatmsg_to_group_instantly("+966535667585", "Hey",)

        sleep(4)
        print(f"Message successfully sent to {phone_number}")
    except Exception as e:
        print(f"Failed to send message to {phone_number}: {e}")

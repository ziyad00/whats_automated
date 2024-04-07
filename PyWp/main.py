from whats import PyWp

pywp = PyWp()

# Send a WhatsApp Message to a Contact
# pywp.send_message("+966535667585", "Hello")
pywp.send_messages_to_multiple_contacts(
    ["+966535667585", "966535667585"], "Hello")

# Send Same Message To Multiple Contacts

# To logout of Whatsapp and close browser
# pywp.close_browser()

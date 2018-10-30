from twilio.rest import Client
import secret_codes


def send_text(text_message):
    account_sid = "ACea9bfc3dfc9065ccf0995aaf72926061"
    auth_token = secret_codes.twilio_token

    client = Client(account_sid, auth_token)
    message = client.messages.create(
                                     body=text_message,
                                     from_='+15302504312',
                                     to='+13108698576'
                                     )
    return message.sid

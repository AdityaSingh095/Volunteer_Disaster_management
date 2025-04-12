from twilio.rest import Client
from config import config
import streamlit as st

def get_twilio_client():
    """Get Twilio client"""
    return Client(config["TWILIO_ACCOUNT_SID"], config["TWILIO_AUTH_TOKEN"])

def send_sms(to, message):
    """Send SMS using Twilio"""
    try:
        client = get_twilio_client()
        msg = client.messages.create(
            body=message,
            from_=config["TWILIO_PHONE_NUMBER"],
            to=to
        )
        return f"SMS sent successfully to {to}: {msg.sid}"
    except Exception as e:
        st.error(f"Error sending SMS: {e}")
        return f"Failed to send SMS: {str(e)}"

def notify_emergency_services(location, severity, user_phone):
    """Notify emergency services and user via SMS"""
    government_contact = "+919625984260"  # Emergency services number
    try:
        # Message to emergency services
        gov_message = f"🚨 URGENT! Emergency at {location}. Severity: {severity}. Immediate response required."
        gov_status = send_sms(government_contact, gov_message)

        # Message to user
        user_message = f"🔹 Help is on the way! Authorities have been alerted to your emergency at {location} (Severity: {severity}). Stay safe!"
        user_status = send_sms(user_phone, user_message)

        return gov_status, user_status
    except Exception as e:
        st.error(f"Notification error: {e}")
        return f"Failed to notify: {str(e)}", ""

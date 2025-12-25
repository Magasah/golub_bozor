"""
Utility functions for GolubBozor
"""
import requests
import logging
import os

logger = logging.getLogger(__name__)

# Telegram Bot Token - Replace with your actual token
TELEGRAM_BOT_TOKEN = "8184229746:AAFIlY6d284Ti1-wqGrRi09-d97M1Xn2eYU"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"


def send_telegram_message(chat_id, text, image_path=None):
    """
    Send a message to a Telegram user or channel via Bot API
    Supports sending photos with captions
    
    Args:
        chat_id (str): Telegram chat ID or channel username (e.g., '@GolubBozorChannel')
        text (str): Message text to send (caption if image is provided)
        image_path (str, optional): Absolute path to image file to send
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    if not chat_id:
        logger.warning("Cannot send Telegram message: chat_id is empty")
        return False
    
    try:
        # Send with photo if image_path is provided
        if image_path and os.path.isfile(image_path):
            with open(image_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {
                    'chat_id': chat_id,
                    'caption': text,
                    'parse_mode': 'Markdown'  # Use Markdown for photos
                }
                
                response = requests.post(TELEGRAM_PHOTO_URL, data=data, files=files, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"Telegram photo sent successfully to: {chat_id}")
                    return True
                else:
                    logger.error(f"Failed to send Telegram photo. Status: {response.status_code}, Response: {response.text}")
                    return False
        else:
            # Send text-only message
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'  # Support HTML formatting
            }
            
            response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent successfully to: {chat_id}")
                return True
            else:
                logger.error(f"Failed to send Telegram message. Status: {response.status_code}, Response: {response.text}")
                return False
            
    except requests.exceptions.Timeout:
        logger.error("Telegram API request timed out")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram message: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in send_telegram_message: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in send_telegram_message: {str(e)}")
        return False

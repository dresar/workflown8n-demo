"""
WhatsApp Cloud API Integration Module
Handles sending messages via Meta's WhatsApp Cloud API.
"""
import requests
from typing import Dict, Any, Optional
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Wrapper for WhatsApp Cloud API (Meta).
    Supports sending text messages, media, and templates.
    """
    
    def __init__(self, access_token: str, phone_number_id: str = None):
        """
        Initialize WhatsApp service.
        
        Args:
            access_token: WhatsApp API access token
            phone_number_id: Phone number ID from Meta Business
        """
        if not access_token:
            raise ValueError("WhatsApp access token is required")
        
        self.access_token = access_token
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_url = settings.WHATSAPP_API_URL
        
        if not self.phone_number_id:
            logger.warning("WhatsApp phone number ID not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send a text message.
        
        Args:
            to: Recipient phone number (with country code, e.g., "6281234567890")
            message: Message text
        
        Returns:
            Dict with success status and message info
        """
        try:
            if not self.phone_number_id:
                return {
                    'success': False,
                    'error': 'Phone number ID not configured'
                }
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"WhatsApp message sent successfully to {to}")
                
                return {
                    'success': True,
                    'message_id': data.get('messages', [{}])[0].get('id'),
                    'to': to,
                    'status': 'sent'
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"WhatsApp API error: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
        
        except Exception as e:
            error_msg = f"WhatsApp send error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def send_template_message(self, to: str, template_name: str, 
                            language_code: str = "en_US",
                            parameters: Optional[list] = None) -> Dict[str, Any]:
        """
        Send a template message.
        
        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language_code: Template language (default: en_US)
            parameters: List of parameter values for template
        
        Returns:
            Dict with success status and message info
        """
        try:
            if not self.phone_number_id:
                return {
                    'success': False,
                    'error': 'Phone number ID not configured'
                }
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            # Build template parameters
            template_components = []
            if parameters:
                template_components.append({
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in parameters]
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    },
                    "components": template_components
                }
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"WhatsApp template message sent to {to}")
                
                return {
                    'success': True,
                    'message_id': data.get('messages', [{}])[0].get('id'),
                    'to': to,
                    'template': template_name
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"WhatsApp template error: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
        
        except Exception as e:
            error_msg = f"WhatsApp template send error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def send_media_message(self, to: str, media_type: str, media_id: str,
                          caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a media message (image, video, audio, document).
        
        Args:
            to: Recipient phone number
            media_type: Type of media ('image', 'video', 'audio', 'document')
            media_id: Media ID from WhatsApp upload
            caption: Optional caption for image/video
        
        Returns:
            Dict with success status and message info
        """
        try:
            if not self.phone_number_id:
                return {
                    'success': False,
                    'error': 'Phone number ID not configured'
                }
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            media_payload = {
                "id": media_id
            }
            
            if caption and media_type in ['image', 'video']:
                media_payload['caption'] = caption
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": media_type,
                media_type: media_payload
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"WhatsApp media message sent to {to}")
                
                return {
                    'success': True,
                    'message_id': data.get('messages', [{}])[0].get('id'),
                    'to': to,
                    'media_type': media_type
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"WhatsApp media error: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
        
        except Exception as e:
            error_msg = f"WhatsApp media send error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the delivery status of a message.
        
        Args:
            message_id: Message ID from send response
        
        Returns:
            Dict with status information
        """
        try:
            # Note: This endpoint may require business account verification
            url = f"{self.api_url}/{message_id}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not retrieve message status',
                    'status_code': response.status_code
                }
        
        except Exception as e:
            logger.error(f"Error getting message status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


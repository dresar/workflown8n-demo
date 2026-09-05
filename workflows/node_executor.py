"""
Node Executor Module
Handles execution of individual workflow nodes.
"""
from typing import Dict, Any
import logging
from django.conf import settings
from workflows.services.ai_service import AIServiceFactory
from workflows.services.google_service import GoogleServiceFactory
from workflows.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class NodeExecutor:
    """
    Executes individual workflow nodes based on their type.
    """
    
    def __init__(self, node, user):
        """
        Initialize node executor.
        
        Args:
            node: Node model instance
            user: User who owns the workflow
        """
        self.node = node
        self.user = user
        self.config = node.config
    
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        Execute the node with given input data.
        
        Args:
            input_data: Data from previous node or trigger
        
        Returns:
            Dict with 'success', 'output', and optional 'error'
        """
        node_type = self.node.node_type
        
        logger.info(f"Executing node: {self.node.name} (type: {node_type})")
        
        try:
            # Route to appropriate handler
            if node_type == 'gemini':
                return self._execute_gemini(input_data)
            elif node_type == 'groq':
                return self._execute_groq(input_data)
            elif node_type == 'google_sheets_read':
                return self._execute_sheets_read(input_data)
            elif node_type == 'google_sheets_write':
                return self._execute_sheets_write(input_data)
            elif node_type == 'google_docs_create':
                return self._execute_docs_create(input_data)
            elif node_type == 'google_docs_append':
                return self._execute_docs_append(input_data)
            elif node_type == 'google_drive_upload':
                return self._execute_drive_upload(input_data)
            elif node_type == 'google_drive_list':
                return self._execute_drive_list(input_data)
            elif node_type == 'google_photos_upload':
                return self._execute_photos_upload(input_data)
            elif node_type == 'google_photos_list':
                return self._execute_photos_list(input_data)
            elif node_type == 'whatsapp_send':
                return self._execute_whatsapp_send(input_data)
            elif node_type == 'data_transform':
                return self._execute_data_transform(input_data)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported node type: {node_type}'
                }
        
        except Exception as e:
            error_msg = f"Node execution error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _replace_placeholders(self, text: str, input_data: Any) -> str:
        """
        Replace {{input}} placeholders with actual input data.
        
        Args:
            text: Text with placeholders
            input_data: Data to insert
        
        Returns:
            Text with placeholders replaced
        """
        if isinstance(input_data, str):
            return text.replace('{{input}}', input_data)
        elif isinstance(input_data, dict):
            for key, value in input_data.items():
                text = text.replace(f'{{{{{key}}}}}', str(value))
        return text
    
    # AI Service Executors
    
    def _execute_gemini(self, input_data: Any) -> Dict[str, Any]:
        """Execute Gemini AI node"""
        try:
            profile = self.user.profile
            api_key = profile.get_gemini_key()
            
            if not api_key:
                return {'success': False, 'error': 'Gemini API key not configured'}
            
            service = AIServiceFactory.create('gemini', api_key)
            
            prompt = self.config.get('prompt', '{{input}}')
            prompt = self._replace_placeholders(prompt, input_data)
            
            model = self.config.get('model', 'gemini-pro')
            temperature = self.config.get('temperature', 0.7)
            max_tokens = self.config.get('max_tokens', 1024)
            
            result = service.generate_text(prompt, model, temperature, max_tokens)
            
            if result['success']:
                return {
                    'success': True,
                    'output': result['text']
                }
            else:
                return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_groq(self, input_data: Any) -> Dict[str, Any]:
        """Execute Groq AI node"""
        try:
            profile = self.user.profile
            api_key = profile.get_groq_key()
            
            if not api_key:
                return {'success': False, 'error': 'Groq API key not configured'}
            
            service = AIServiceFactory.create('groq', api_key)
            
            prompt = self.config.get('prompt', '{{input}}')
            prompt = self._replace_placeholders(prompt, input_data)
            
            model = self.config.get('model', 'mixtral-8x7b-32768')
            temperature = self.config.get('temperature', 0.7)
            max_tokens = self.config.get('max_tokens', 1024)
            system_message = self.config.get('system_message')
            
            result = service.generate_text(prompt, model, temperature, max_tokens, system_message)
            
            if result['success']:
                return {
                    'success': True,
                    'output': result['text']
                }
            else:
                return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Google Services Executors
    
    def _get_google_credentials(self):
        """Get Google credentials for user"""
        from accounts.models import Credential
        
        try:
            cred = Credential.objects.get(user=self.user, provider='google')
            
            credentials = GoogleServiceFactory.create_credentials(
                access_token=cred.get_access_token(),
                refresh_token=cred.get_refresh_token(),
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
            
            return credentials
        except Credential.DoesNotExist:
            raise Exception("Google credentials not found. Please connect your Google account.")
    
    def _execute_sheets_read(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Sheets read node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('sheets', credentials)
            
            spreadsheet_id = self.config.get('spreadsheet_id')
            range_name = self.config.get('range', 'Sheet1!A1:Z1000')
            
            result = service.read_range(spreadsheet_id, range_name)
            
            if result['success']:
                return {
                    'success': True,
                    'output': result['data']
                }
            else:
                return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_sheets_write(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Sheets write node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('sheets', credentials)
            
            spreadsheet_id = self.config.get('spreadsheet_id')
            range_name = self.config.get('range', 'Sheet1!A1')
            
            # Convert input_data to 2D array if needed
            if isinstance(input_data, str):
                values = [[input_data]]
            elif isinstance(input_data, list):
                if input_data and not isinstance(input_data[0], list):
                    values = [input_data]
                else:
                    values = input_data
            else:
                values = [[str(input_data)]]
            
            result = service.write_range(spreadsheet_id, range_name, values)
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_docs_create(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Docs create node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('docs', credentials)
            
            title = self.config.get('title', 'Untitled Document')
            title = self._replace_placeholders(title, input_data)
            
            result = service.create_document(title)
            
            # If there's content to add, append it
            if result['success'] and input_data:
                content = str(input_data)
                append_result = service.append_text(result['document_id'], content)
                if not append_result['success']:
                    result['warning'] = 'Document created but failed to add content'
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_docs_append(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Docs append node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('docs', credentials)
            
            document_id = self.config.get('document_id')
            text = self.config.get('text', '{{input}}')
            text = self._replace_placeholders(text, input_data)
            
            result = service.append_text(document_id, text)
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_drive_upload(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Drive upload node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('drive', credentials)
            
            file_path = self.config.get('file_path')
            file_name = self.config.get('file_name')
            mime_type = self.config.get('mime_type')
            
            result = service.upload_file(file_path, file_name, mime_type)
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_drive_list(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Drive list node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('drive', credentials)
            
            query = self.config.get('query')
            max_results = self.config.get('max_results', 10)
            
            result = service.list_files(query, max_results)
            
            if result['success']:
                return {
                    'success': True,
                    'output': result['files']
                }
            else:
                return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_photos_upload(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Photos upload node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('photos', credentials)
            
            file_path = self.config.get('file_path')
            description = self.config.get('description')
            
            result = service.upload_photo(file_path, description)
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_photos_list(self, input_data: Any) -> Dict[str, Any]:
        """Execute Google Photos list node"""
        try:
            credentials = self._get_google_credentials()
            service = GoogleServiceFactory.create_service('photos', credentials)
            
            max_results = self.config.get('max_results', 10)
            
            result = service.list_media_items(max_results)
            
            if result['success']:
                return {
                    'success': True,
                    'output': result['items']
                }
            else:
                return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # WhatsApp Executor
    
    def _execute_whatsapp_send(self, input_data: Any) -> Dict[str, Any]:
        """Execute WhatsApp send node"""
        try:
            profile = self.user.profile
            token = profile.get_whatsapp_token()
            
            if not token:
                return {'success': False, 'error': 'WhatsApp token not configured'}
            
            phone_number_id = self.config.get('phone_number_id')
            service = WhatsAppService(token, phone_number_id)
            
            to = self.config.get('to')
            message = self.config.get('message', '{{input}}')
            message = self._replace_placeholders(message, input_data)
            
            result = service.send_text_message(to, message)
            
            return result
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Utility Executor
    
    def _execute_data_transform(self, input_data: Any) -> Dict[str, Any]:
        """Execute data transformation node"""
        try:
            # Simple transformation logic
            transform_type = self.config.get('transform_type', 'passthrough')
            
            if transform_type == 'passthrough':
                return {'success': True, 'output': input_data}
            elif transform_type == 'to_json':
                import json
                return {'success': True, 'output': json.dumps(input_data)}
            elif transform_type == 'to_string':
                return {'success': True, 'output': str(input_data)}
            elif transform_type == 'to_list':
                if isinstance(input_data, list):
                    return {'success': True, 'output': input_data}
                else:
                    return {'success': True, 'output': [input_data]}
            else:
                return {'success': False, 'error': f'Unknown transform type: {transform_type}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


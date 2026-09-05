"""
Google Services Integration Module
Handles OAuth2 authentication and API calls to Google services:
- Google Sheets
- Google Docs
- Google Drive
- Google Photos
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """
    Handles Google OAuth2 authentication flow.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/photoslibrary',
    ]
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize OAuth service.
        
        Args:
            client_id: Google OAuth2 client ID
            client_secret: Google OAuth2 client secret
            redirect_uri: Redirect URI for OAuth callback
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Get the authorization URL for user to grant permissions.
        
        Args:
            state: Optional state parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from callback
        
        Returns:
            Dict with tokens and expiry information
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            return {
                'success': True,
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None,
                'scopes': credentials.scopes
            }
        
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Dict with new access token and expiry
        """
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )
            
            credentials.refresh(Request())
            
            return {
                'success': True,
                'access_token': credentials.token,
                'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
        
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GoogleSheetsService:
    """
    Google Sheets API wrapper.
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize Sheets service with credentials.
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def read_range(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """
        Read data from a spreadsheet range.
        
        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: Range in A1 notation (e.g., 'Sheet1!A1:C10')
        
        Returns:
            Dict with success status and data
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            return {
                'success': True,
                'data': values,
                'rows': len(values),
                'range': range_name
            }
        
        except Exception as e:
            logger.error(f"Error reading from Sheets: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def write_range(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """
        Write data to a spreadsheet range.
        
        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: Range in A1 notation
            values: 2D list of values to write
        
        Returns:
            Dict with success status and update info
        """
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                'success': True,
                'updated_cells': result.get('updatedCells'),
                'updated_rows': result.get('updatedRows'),
                'updated_columns': result.get('updatedColumns')
            }
        
        except Exception as e:
            logger.error(f"Error writing to Sheets: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def append_rows(self, spreadsheet_id: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """
        Append rows to the end of a sheet.
        
        Args:
            spreadsheet_id: The spreadsheet ID
            range_name: Range in A1 notation
            values: 2D list of values to append
        
        Returns:
            Dict with success status and update info
        """
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return {
                'success': True,
                'updated_cells': result.get('updates', {}).get('updatedCells'),
                'updated_range': result.get('updates', {}).get('updatedRange')
            }
        
        except Exception as e:
            logger.error(f"Error appending to Sheets: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GoogleDocsService:
    """
    Google Docs API wrapper.
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize Docs service with credentials.
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.service = build('docs', 'v1', credentials=credentials)
    
    def create_document(self, title: str) -> Dict[str, Any]:
        """
        Create a new Google Doc.
        
        Args:
            title: Document title
        
        Returns:
            Dict with success status and document info
        """
        try:
            doc = self.service.documents().create(body={'title': title}).execute()
            
            return {
                'success': True,
                'document_id': doc.get('documentId'),
                'title': doc.get('title'),
                'url': f"https://docs.google.com/document/d/{doc.get('documentId')}/edit"
            }
        
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def append_text(self, document_id: str, text: str) -> Dict[str, Any]:
        """
        Append text to the end of a document.
        
        Args:
            document_id: The document ID
            text: Text to append
        
        Returns:
            Dict with success status
        """
        try:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': text
                    }
                }
            ]
            
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return {
                'success': True,
                'document_id': document_id
            }
        
        except Exception as e:
            logger.error(f"Error appending text to document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_document_content(self, document_id: str) -> Dict[str, Any]:
        """
        Get document content.
        
        Args:
            document_id: The document ID
        
        Returns:
            Dict with success status and content
        """
        try:
            doc = self.service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = []
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for text_run in element['paragraph'].get('elements', []):
                        if 'textRun' in text_run:
                            content.append(text_run['textRun'].get('content', ''))
            
            return {
                'success': True,
                'document_id': document_id,
                'title': doc.get('title'),
                'content': ''.join(content)
            }
        
        except Exception as e:
            logger.error(f"Error getting document content: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GoogleDriveService:
    """
    Google Drive API wrapper.
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize Drive service with credentials.
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.service = build('drive', 'v3', credentials=credentials)
    
    def list_files(self, query: str = None, max_results: int = 10) -> Dict[str, Any]:
        """
        List files in Drive.
        
        Args:
            query: Search query (e.g., "name contains 'report'")
            max_results: Maximum number of results
        
        Returns:
            Dict with success status and file list
        """
        try:
            params = {
                'pageSize': max_results,
                'fields': 'files(id, name, mimeType, createdTime, modifiedTime, size)',
            }
            
            if query:
                params['q'] = query
            
            results = self.service.files().list(**params).execute()
            files = results.get('files', [])
            
            return {
                'success': True,
                'files': files,
                'count': len(files)
            }
        
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_file(self, file_path: str, file_name: str = None, mime_type: str = None) -> Dict[str, Any]:
        """
        Upload a file to Drive.
        
        Args:
            file_path: Path to the file
            file_name: Name for the file in Drive (defaults to original name)
            mime_type: MIME type of the file
        
        Returns:
            Dict with success status and file info
        """
        try:
            if not file_name:
                file_name = file_path.split('/')[-1]
            
            file_metadata = {'name': file_name}
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'name': file.get('name'),
                'url': file.get('webViewLink')
            }
        
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GooglePhotosService:
    """
    Google Photos API wrapper.
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize Photos service with credentials.
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.service = build('photoslibrary', 'v1', credentials=credentials, static_discovery=False)
    
    def list_media_items(self, max_results: int = 10) -> Dict[str, Any]:
        """
        List media items (photos/videos).
        
        Args:
            max_results: Maximum number of results
        
        Returns:
            Dict with success status and media items
        """
        try:
            results = self.service.mediaItems().list(pageSize=max_results).execute()
            media_items = results.get('mediaItems', [])
            
            items = []
            for item in media_items:
                items.append({
                    'id': item.get('id'),
                    'filename': item.get('filename'),
                    'mime_type': item.get('mimeType'),
                    'created_time': item.get('mediaMetadata', {}).get('creationTime'),
                    'base_url': item.get('baseUrl')
                })
            
            return {
                'success': True,
                'items': items,
                'count': len(items)
            }
        
        except Exception as e:
            logger.error(f"Error listing media items: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_photo(self, file_path: str, description: str = None) -> Dict[str, Any]:
        """
        Upload a photo to Google Photos.
        
        Args:
            file_path: Path to the photo file
            description: Optional description
        
        Returns:
            Dict with success status and upload info
        """
        try:
            # Note: Google Photos API upload is complex and requires raw bytes upload first
            # This is a simplified version
            with open(file_path, 'rb') as f:
                upload_token = self.service.mediaItems().upload(
                    body=f.read()
                ).execute()
            
            # Create media item
            new_media_item = {
                'newMediaItems': [
                    {
                        'simpleMediaItem': {
                            'uploadToken': upload_token
                        },
                        'description': description or ''
                    }
                ]
            }
            
            result = self.service.mediaItems().batchCreate(
                body=new_media_item
            ).execute()
            
            return {
                'success': True,
                'result': result
            }
        
        except Exception as e:
            logger.error(f"Error uploading photo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class GoogleServiceFactory:
    """
    Factory to create Google service instances.
    """
    
    @staticmethod
    def create_credentials(access_token: str, refresh_token: str,
                          client_id: str, client_secret: str) -> Credentials:
        """
        Create Google credentials object.
        
        Args:
            access_token: Access token
            refresh_token: Refresh token
            client_id: Client ID
            client_secret: Client secret
        
        Returns:
            Credentials object
        """
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=GoogleOAuthService.SCOPES
        )
    
    @staticmethod
    def create_service(service_type: str, credentials: Credentials):
        """
        Create a Google service instance.
        
        Args:
            service_type: 'sheets', 'docs', 'drive', or 'photos'
            credentials: Google OAuth2 credentials
        
        Returns:
            Service instance
        
        Raises:
            ValueError: If service type is not supported
        """
        service_type = service_type.lower()
        
        if service_type == 'sheets':
            return GoogleSheetsService(credentials)
        elif service_type == 'docs':
            return GoogleDocsService(credentials)
        elif service_type == 'drive':
            return GoogleDriveService(credentials)
        elif service_type == 'photos':
            return GooglePhotosService(credentials)
        else:
            raise ValueError(f"Unsupported service type: {service_type}")


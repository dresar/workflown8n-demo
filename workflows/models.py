from django.db import models
from django.contrib.auth.models import User
import json
import uuid


class Workflow(models.Model):
    """
    Main Workflow model - represents an automation workflow.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Whether the workflow is active")
    
    # Webhook trigger
    webhook_token = models.CharField(max_length=100, unique=True, blank=True, help_text="Unique token for webhook URL")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Generate webhook token if not exists"""
        if not self.webhook_token:
            self.webhook_token = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def get_webhook_url(self, request=None):
        """Get the full webhook URL"""
        if request:
            return request.build_absolute_uri(f'/webhook/{self.webhook_token}/')
        return f'/webhook/{self.webhook_token}/'
    
    def execute(self, input_data=None):
        """
        Execute the workflow by running all nodes in sequence.
        Returns the final output and creates an ExecutionLog.
        """
        from workflows.executor import WorkflowExecutor
        executor = WorkflowExecutor(self)
        return executor.execute(input_data)


class Node(models.Model):
    """
    Represents a single step/node in a workflow.
    Each node performs a specific action (e.g., call API, process data).
    """
    NODE_TYPES = [
        # AI Services
        ('gemini', 'Gemini AI'),
        ('groq', 'Groq AI'),
        
        # Google Services
        ('google_sheets_read', 'Google Sheets - Read'),
        ('google_sheets_write', 'Google Sheets - Write'),
        ('google_docs_create', 'Google Docs - Create'),
        ('google_docs_append', 'Google Docs - Append'),
        ('google_drive_upload', 'Google Drive - Upload'),
        ('google_drive_list', 'Google Drive - List'),
        ('google_photos_upload', 'Google Photos - Upload'),
        ('google_photos_list', 'Google Photos - List'),
        
        # Messaging
        ('whatsapp_send', 'WhatsApp - Send Message'),
        
        # Utilities
        ('webhook_trigger', 'Webhook Trigger'),
        ('data_transform', 'Data Transform'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    node_type = models.CharField(max_length=50, choices=NODE_TYPES)
    name = models.CharField(max_length=255, help_text="Custom name for this node")
    
    # Node position in workflow
    order = models.IntegerField(default=0, help_text="Execution order in the workflow")
    
    # Configuration stored as JSON
    # Example: {"prompt": "Analyze this", "model": "gemini-pro"}
    config = models.JSONField(default=dict, help_text="Node configuration as JSON")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Node"
        verbose_name_plural = "Nodes"
        ordering = ['workflow', 'order']
    
    def __str__(self):
        return f"{self.workflow.title} - {self.name}"
    
    def execute(self, input_data, user):
        """
        Execute this node with given input data.
        Returns the output to be passed to next node.
        """
        from workflows.node_executor import NodeExecutor
        executor = NodeExecutor(self, user)
        return executor.execute(input_data)


class ExecutionLog(models.Model):
    """
    Stores the execution history of workflows.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='execution_logs')
    
    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Input/Output data
    input_data = models.JSONField(blank=True, null=True, help_text="Input data that triggered the workflow")
    output_data = models.JSONField(blank=True, null=True, help_text="Final output of the workflow")
    error_message = models.TextField(blank=True, help_text="Error message if execution failed")
    
    # Node execution details
    node_results = models.JSONField(default=list, help_text="Results from each node execution")
    
    class Meta:
        verbose_name = "Execution Log"
        verbose_name_plural = "Execution Logs"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.workflow.title} - {self.status} at {self.started_at}"
    
    def add_node_result(self, node_name, node_type, success, output=None, error=None):
        """Add a node execution result to the log"""
        result = {
            'node_name': node_name,
            'node_type': node_type,
            'success': success,
            'output': output,
            'error': error,
            'timestamp': str(self.started_at)
        }
        if not isinstance(self.node_results, list):
            self.node_results = []
        self.node_results.append(result)
        self.save()
    
    def duration(self):
        """Calculate execution duration"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

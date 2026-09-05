from django.contrib import admin
from .models import Workflow, Node, ExecutionLog


class NodeInline(admin.TabularInline):
    model = Node
    extra = 1
    fields = ['name', 'node_type', 'order', 'config']
    ordering = ['order']


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_active', 'created_at', 'last_run_at']
    list_filter = ['is_active', 'created_at', 'owner']
    search_fields = ['title', 'description', 'owner__username']
    readonly_fields = ['id', 'webhook_token', 'created_at', 'updated_at', 'last_run_at']
    inlines = [NodeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'title', 'description', 'is_active')
        }),
        ('Webhook Configuration', {
            'fields': ('webhook_token',),
            'description': 'Unique token for triggering this workflow via webhook'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'last_run_at'),
        }),
    )


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'node_type', 'order', 'created_at']
    list_filter = ['node_type', 'created_at']
    search_fields = ['name', 'workflow__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Node Information', {
            'fields': ('workflow', 'name', 'node_type', 'order')
        }),
        ('Configuration', {
            'fields': ('config',),
            'description': 'JSON configuration for this node'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
        }),
    )


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'status', 'started_at', 'completed_at', 'duration_display']
    list_filter = ['status', 'started_at']
    search_fields = ['workflow__title']
    readonly_fields = ['id', 'started_at', 'completed_at', 'duration_display']
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('workflow', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_display')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data', 'error_message', 'node_results')
        }),
        ('Metadata', {
            'fields': ('id',),
        }),
    )
    
    def duration_display(self, obj):
        """Display execution duration"""
        duration = obj.duration()
        if duration:
            return f"{duration:.2f} seconds"
        return "Running..." if obj.status == 'running' else "-"
    duration_display.short_description = "Duration"

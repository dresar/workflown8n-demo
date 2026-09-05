from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from workflows.models import Workflow, Node, ExecutionLog
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Dashboard showing all workflows"""
    workflows = Workflow.objects.filter(owner=request.user).order_by('-created_at')
    
    # Get recent execution logs
    recent_logs = ExecutionLog.objects.filter(
        workflow__owner=request.user
    ).order_by('-started_at')[:10]
    
    context = {
        'workflows': workflows,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'workflows/dashboard.html', context)


@login_required
def workflow_create_view(request):
    """Create a new workflow"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if not title:
            messages.error(request, 'Workflow title is required')
            return render(request, 'workflows/create.html')
        
        workflow = Workflow.objects.create(
            owner=request.user,
            title=title,
            description=description
        )
        
        messages.success(request, f'Workflow "{title}" created successfully!')
        return redirect('workflow_edit', workflow_id=workflow.id)
    
    return render(request, 'workflows/create.html')


@login_required
def workflow_edit_view(request, workflow_id):
    """Edit workflow and manage nodes"""
    workflow = get_object_or_404(Workflow, id=workflow_id, owner=request.user)
    nodes = workflow.nodes.all().order_by('order')
    
    if request.method == 'POST':
        # Update workflow details
        workflow.title = request.POST.get('title', workflow.title)
        workflow.description = request.POST.get('description', workflow.description)
        workflow.is_active = request.POST.get('is_active') == 'on'
        workflow.save()
        
        messages.success(request, 'Workflow updated successfully!')
        return redirect('workflow_edit', workflow_id=workflow.id)
    
    # Get node type choices for the form
    node_types = Node.NODE_TYPES
    
    context = {
        'workflow': workflow,
        'nodes': nodes,
        'node_types': node_types,
        'webhook_url': workflow.get_webhook_url(request),
    }
    
    return render(request, 'workflows/edit.html', context)


@login_required
def workflow_delete_view(request, workflow_id):
    """Delete a workflow"""
    workflow = get_object_or_404(Workflow, id=workflow_id, owner=request.user)
    
    if request.method == 'POST':
        title = workflow.title
        workflow.delete()
        messages.success(request, f'Workflow "{title}" deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'workflows/delete_confirm.html', {'workflow': workflow})


@login_required
def node_create_view(request, workflow_id):
    """Create a new node in workflow"""
    workflow = get_object_or_404(Workflow, id=workflow_id, owner=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        node_type = request.POST.get('node_type')
        config_str = request.POST.get('config', '{}')
        
        if not all([name, node_type]):
            messages.error(request, 'Node name and type are required')
            return redirect('workflow_edit', workflow_id=workflow.id)
        
        try:
            config = json.loads(config_str)
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON configuration')
            return redirect('workflow_edit', workflow_id=workflow.id)
        
        # Get the next order number
        last_node = workflow.nodes.order_by('-order').first()
        order = (last_node.order + 1) if last_node else 0
        
        node = Node.objects.create(
            workflow=workflow,
            name=name,
            node_type=node_type,
            config=config,
            order=order
        )
        
        messages.success(request, f'Node "{name}" added successfully!')
        return redirect('workflow_edit', workflow_id=workflow.id)
    
    return redirect('workflow_edit', workflow_id=workflow.id)


@login_required
def node_edit_view(request, node_id):
    """Edit a node"""
    node = get_object_or_404(Node, id=node_id, workflow__owner=request.user)
    
    if request.method == 'POST':
        node.name = request.POST.get('name', node.name)
        node.node_type = request.POST.get('node_type', node.node_type)
        
        config_str = request.POST.get('config', '{}')
        try:
            node.config = json.loads(config_str)
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON configuration')
            return redirect('workflow_edit', workflow_id=node.workflow.id)
        
        node.save()
        messages.success(request, f'Node "{node.name}" updated successfully!')
        return redirect('workflow_edit', workflow_id=node.workflow.id)
    
    context = {
        'node': node,
        'node_types': Node.NODE_TYPES,
        'config_json': json.dumps(node.config, indent=2)
    }
    
    return render(request, 'workflows/node_edit.html', context)


@login_required
def node_delete_view(request, node_id):
    """Delete a node"""
    node = get_object_or_404(Node, id=node_id, workflow__owner=request.user)
    workflow_id = node.workflow.id
    
    if request.method == 'POST':
        node.delete()
        messages.success(request, 'Node deleted successfully!')
    
    return redirect('workflow_edit', workflow_id=workflow_id)


@login_required
def workflow_run_view(request, workflow_id):
    """Manually run a workflow"""
    workflow = get_object_or_404(Workflow, id=workflow_id, owner=request.user)
    
    if request.method == 'POST':
        # Get input data from form
        input_data_str = request.POST.get('input_data', '{}')
        
        try:
            input_data = json.loads(input_data_str) if input_data_str else {}
        except json.JSONDecodeError:
            messages.error(request, 'Invalid JSON input data')
            return redirect('workflow_edit', workflow_id=workflow.id)
        
        # Execute workflow
        result = workflow.execute(input_data)
        
        if result.get('success'):
            messages.success(request, f'Workflow executed successfully! Execution ID: {result["execution_id"]}')
        else:
            messages.error(request, f'Workflow execution failed: {result.get("error")}')
        
        return redirect('execution_log_detail', log_id=result['execution_id'])
    
    return redirect('workflow_edit', workflow_id=workflow.id)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def webhook_trigger_view(request, token):
    """Webhook endpoint to trigger workflow"""
    try:
        workflow = Workflow.objects.get(webhook_token=token, is_active=True)
    except Workflow.DoesNotExist:
        return JsonResponse({'error': 'Workflow not found or inactive'}, status=404)
    
    # Get input data from request
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                input_data = json.loads(request.body)
            else:
                input_data = dict(request.POST)
        except json.JSONDecodeError:
            input_data = {'raw': request.body.decode('utf-8')}
    else:
        input_data = dict(request.GET)
    
    logger.info(f"Webhook triggered for workflow: {workflow.title}")
    
    # Execute workflow
    result = workflow.execute(input_data)
    
    if result.get('success'):
        return JsonResponse({
            'success': True,
            'execution_id': result['execution_id'],
            'output': result.get('output')
        })
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error'),
            'execution_id': result.get('execution_id')
        }, status=500)


@login_required
def execution_logs_view(request):
    """View all execution logs"""
    logs = ExecutionLog.objects.filter(
        workflow__owner=request.user
    ).order_by('-started_at')
    
    # Filter by workflow if specified
    workflow_id = request.GET.get('workflow')
    if workflow_id:
        logs = logs.filter(workflow_id=workflow_id)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        logs = logs.filter(status=status)
    
    context = {
        'logs': logs,
        'workflows': Workflow.objects.filter(owner=request.user),
    }
    
    return render(request, 'workflows/execution_logs.html', context)


@login_required
def execution_log_detail_view(request, log_id):
    """View detailed execution log"""
    log = get_object_or_404(ExecutionLog, id=log_id, workflow__owner=request.user)
    
    context = {
        'log': log,
    }
    
    return render(request, 'workflows/execution_log_detail.html', context)

"""
Workflow Executor Module
Handles execution of complete workflows by chaining nodes.
"""
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Executes complete workflows by running nodes in sequence.
    """
    
    def __init__(self, workflow):
        """
        Initialize workflow executor.
        
        Args:
            workflow: Workflow model instance
        """
        self.workflow = workflow
        self.user = workflow.owner
    
    def execute(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute the workflow.
        
        Args:
            input_data: Initial input data for the workflow
        
        Returns:
            Dict with execution results
        """
        from workflows.models import ExecutionLog
        
        # Create execution log
        exec_log = ExecutionLog.objects.create(
            workflow=self.workflow,
            status='running',
            input_data=input_data if isinstance(input_data, dict) else {'data': input_data}
        )
        
        logger.info(f"Starting workflow execution: {self.workflow.title} (ID: {exec_log.id})")
        
        try:
            # Get all nodes ordered by execution order
            nodes = self.workflow.nodes.all().order_by('order')
            
            if not nodes.exists():
                exec_log.status = 'error'
                exec_log.error_message = 'No nodes found in workflow'
                exec_log.completed_at = timezone.now()
                exec_log.save()
                
                return {
                    'success': False,
                    'error': 'No nodes found in workflow',
                    'execution_id': str(exec_log.id)
                }
            
            # Execute nodes in sequence
            current_data = input_data
            
            for node in nodes:
                logger.info(f"Executing node: {node.name} (Order: {node.order})")
                
                try:
                    # Execute the node
                    result = node.execute(current_data, self.user)
                    
                    # Log node result
                    exec_log.add_node_result(
                        node_name=node.name,
                        node_type=node.node_type,
                        success=result.get('success', False),
                        output=result.get('output'),
                        error=result.get('error')
                    )
                    
                    if not result.get('success'):
                        # Node failed, stop execution
                        error_msg = result.get('error', 'Unknown error')
                        logger.error(f"Node {node.name} failed: {error_msg}")
                        
                        exec_log.status = 'error'
                        exec_log.error_message = f"Node '{node.name}' failed: {error_msg}"
                        exec_log.completed_at = timezone.now()
                        exec_log.save()
                        
                        return {
                            'success': False,
                            'error': exec_log.error_message,
                            'execution_id': str(exec_log.id),
                            'failed_node': node.name
                        }
                    
                    # Use output as input for next node
                    current_data = result.get('output', current_data)
                    logger.info(f"Node {node.name} completed successfully")
                
                except Exception as e:
                    error_msg = f"Exception in node {node.name}: {str(e)}"
                    logger.error(error_msg)
                    
                    exec_log.add_node_result(
                        node_name=node.name,
                        node_type=node.node_type,
                        success=False,
                        error=str(e)
                    )
                    
                    exec_log.status = 'error'
                    exec_log.error_message = error_msg
                    exec_log.completed_at = timezone.now()
                    exec_log.save()
                    
                    return {
                        'success': False,
                        'error': error_msg,
                        'execution_id': str(exec_log.id),
                        'failed_node': node.name
                    }
            
            # All nodes completed successfully
            exec_log.status = 'success'
            exec_log.output_data = current_data if isinstance(current_data, dict) else {'result': current_data}
            exec_log.completed_at = timezone.now()
            exec_log.save()
            
            # Update workflow last_run_at
            self.workflow.last_run_at = timezone.now()
            self.workflow.save()
            
            logger.info(f"Workflow execution completed successfully: {self.workflow.title}")
            
            return {
                'success': True,
                'output': current_data,
                'execution_id': str(exec_log.id),
                'nodes_executed': nodes.count()
            }
        
        except Exception as e:
            error_msg = f"Workflow execution error: {str(e)}"
            logger.error(error_msg)
            
            exec_log.status = 'error'
            exec_log.error_message = error_msg
            exec_log.completed_at = timezone.now()
            exec_log.save()
            
            return {
                'success': False,
                'error': error_msg,
                'execution_id': str(exec_log.id)
            }


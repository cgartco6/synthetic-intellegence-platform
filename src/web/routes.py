from flask import render_template, request, jsonify, session, send_file
import asyncio
import json
from typing import Dict, Any

def register_routes(app, orchestrator, db):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/api/tasks', methods=['POST'])
    async def create_task():
        """Create a new AI task"""
        try:
            data = request.get_json()
            task_type = data.get('type')
            payload = data.get('payload', {})
            agent_name = data.get('agent')
            
            if not task_type:
                return jsonify({'error': 'Task type is required'}), 400
            
            task = await orchestrator.submit_task(task_type, payload, agent_name)
            
            if task:
                return jsonify({
                    'task_id': task.id,
                    'status': 'submitted',
                    'message': f'Task {task.id} submitted successfully'
                })
            else:
                return jsonify({'error': 'Failed to submit task'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tasks/<task_id>')
    def get_task(task_id):
        """Get task status and result"""
        task = None
        
        # Check all agents for the task
        for agent in orchestrator.agents.values():
            task = agent.get_task(task_id)
            if task:
                break
        
        if task:
            return jsonify(task.to_dict())
        else:
            return jsonify({'error': 'Task not found'}), 404
    
    @app.route('/api/tasks')
    def list_tasks():
        """List all tasks"""
        all_tasks = []
        
        for agent in orchestrator.agents.values():
            agent_tasks = agent.get_tasks()
            all_tasks.extend([task.to_dict() for task in agent_tasks])
        
        return jsonify({'tasks': all_tasks})
    
    @app.route('/api/projects', methods=['POST'])
    def create_project():
        """Create a new project"""
        try:
            data = request.get_json()
            name = data.get('name')
            project_type = data.get('type')
            config = data.get('config', {})
            
            if not name or not project_type:
                return jsonify({'error': 'Name and type are required'}), 400
            
            project_id = db.create_project(name, project_type, config)
            
            if project_id > 0:
                return jsonify({
                    'project_id': project_id,
                    'message': f'Project {name} created successfully'
                })
            else:
                return jsonify({'error': 'Failed to create project'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/projects')
    def list_projects():
        """List all projects"""
        projects = db.get_projects()
        return jsonify({'projects': projects})
    
    @app.route('/api/content/generate', methods=['POST'])
    async def generate_content():
        """Generate content using AI"""
        try:
            data = request.get_json()
            content_type = data.get('content_type', 'blog_post')
            topic = data.get('topic', '')
            parameters = data.get('parameters', {})
            
            if not topic:
                return jsonify({'error': 'Topic is required'}), 400
            
            payload = {
                'topic': topic,
                **parameters
            }
            
            task = await orchestrator.submit_task(content_type, payload, 'content_creator')
            
            if task:
                # Wait for completion (in production, use WebSocket or polling)
                import time
                max_wait = 30  # seconds
                wait_time = 0
                
                while task.status in ['pending', 'running'] and wait_time < max_wait:
                    time.sleep(0.5)
                    wait_time += 0.5
                    task = orchestrator.get_agent('content_creator').get_task(task.id)
                
                if task.status == 'completed':
                    return jsonify({
                        'status': 'success',
                        'content': task.result
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': task.error or 'Task timed out'
                    }), 500
            else:
                return jsonify({'error': 'Failed to submit content generation task'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social-media/schedule', methods=['POST'])
    async def schedule_social_media_post():
        """Schedule a social media post"""
        try:
            data = request.get_json()
            platform = data.get('platform', 'facebook')
            content = data.get('content', '')
            schedule_time = data.get('schedule_time')
            
            if not content:
                return jsonify({'error': 'Content is required'}), 400
            
            payload = {
                'platform': platform,
                'content': content,
                'schedule_time': schedule_time
            }
            
            task = await orchestrator.submit_task('schedule_post', payload, 'social_media_manager')
            
            if task:
                return jsonify({
                    'task_id': task.id,
                    'status': 'submitted',
                    'message': f'Post scheduled on {platform}'
                })
            else:
                return jsonify({'error': 'Failed to schedule post'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analytics/performance')
    async def get_performance_analytics():
        """Get social media performance analytics"""
        try:
            platform = request.args.get('platform', 'all')
            time_range = request.args.get('time_range', '7d')
            
            payload = {
                'platform': platform,
                'time_range': time_range,
                'metrics': ['engagement', 'reach', 'impressions']
            }
            
            task = await orchestrator.submit_task('analyze_performance', payload, 'social_media_manager')
            
            if task:
                return jsonify({
                    'task_id': task.id,
                    'status': 'submitted',
                    'message': 'Performance analysis started'
                })
            else:
                return jsonify({'error': 'Failed to start analysis'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/system/status')
    def get_system_status():
        """Get system status and metrics"""
        status = orchestrator.get_system_status()
        return jsonify(status)
    
    @app.route('/api/agents')
    def list_agents():
        """List all registered agents and their capabilities"""
        agents_info = {}
        
        for name, agent in orchestrator.agents.items():
            agents_info[name] = {
                'capabilities': agent.capabilities,
                'config': agent.config
            }
        
        return jsonify({'agents': agents_info})

from flask import Flask, render_template, request, jsonify, session, send_file
import asyncio
import logging
from typing import Dict, Any
import json
import os

from .routes import register_routes
from ..agents.orchestrator import AgentOrchestrator
from ..agents.content_creator import ContentCreatorAgent
from ..agents.social_media_manager import SocialMediaManagerAgent
from ..helpers.database import DatabaseManager

class AIPlatformApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
        self.db = DatabaseManager()
        self.orchestrator = AgentOrchestrator()
        
        self._setup_logging()
        self._register_agents()
        self._setup_routes()
        self._start_background_tasks()
    
    def _setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ai_platform")
    
    def _register_agents(self):
        """Register AI agents with orchestrator"""
        # Content Creator Agent
        content_config = {
            'llm': {
                'openai_api_key': os.getenv('OPENAI_API_KEY'),
                'use_local_models': True
            }
        }
        content_agent = ContentCreatorAgent(content_config)
        self.orchestrator.register_agent(content_agent)
        
        # Social Media Manager Agent
        social_config = {
            'api_config': {
                'facebook_app_id': os.getenv('FACEBOOK_APP_ID'),
                'twitter_api_key': os.getenv('TWITTER_API_KEY')
            }
        }
        social_agent = SocialMediaManagerAgent(social_config)
        self.orchestrator.register_agent(social_agent)
        
        self.logger.info("Registered all AI agents")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        register_routes(self.app, self.orchestrator, self.db)
    
    def _start_background_tasks(self):
        """Start background task processing"""
        async def start_orchestrator():
            await self.orchestrator.process_tasks()
        
        # Run in background
        asyncio.create_task(start_orchestrator())
    
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the Flask application"""
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Create and configure the Flask app"""
    platform = AIPlatformApp()
    return platform.app

if __name__ == '__main__':
    app_instance = AIPlatformApp()
    app_instance.run()

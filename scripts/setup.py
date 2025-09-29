#!/usr/bin/env python3
"""
Setup script for Synthetic Intelligence Platform
"""

import os
import sys
import subprocess
import venv
import logging
from pathlib import Path

class PlatformSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.venv_dir = self.root_dir / "venv"
        self.requirements_file = self.root_dir / "requirements.txt"
        
        self._setup_logging()
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("setup")
    
    def create_virtualenv(self):
        """Create virtual environment"""
        self.logger.info("Creating virtual environment...")
        
        if self.venv_dir.exists():
            self.logger.info("Virtual environment already exists")
            return True
        
        try:
            venv.create(self.venv_dir, with_pip=True)
            self.logger.info("Virtual environment created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create virtual environment: {str(e)}")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.logger.info("Installing dependencies...")
        
        pip_path = self.venv_dir / "bin" / "pip"
        if os.name == 'nt':  # Windows
            pip_path = self.venv_dir / "Scripts" / "pip.exe"
        
        try:
            subprocess.run([
                str(pip_path), "install", "-r", str(self.requirements_file)
            ], check=True)
            self.logger.info("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {str(e)}")
            return False
    
    def setup_environment(self):
        """Setup environment variables"""
        self.logger.info("Setting up environment...")
        
        env_example = self.root_dir / ".env.example"
        env_file = self.root_dir / ".env"
        
        if not env_file.exists() and env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            self.logger.info("Created .env file from example")
        
        self.logger.info("Please configure your .env file with API keys and settings")
    
    def initialize_database(self):
        """Initialize the database"""
        self.logger.info("Initializing database...")
        
        try:
            # This will create the database when the app first runs
            from src.helpers.database import DatabaseManager
            db = DatabaseManager()
            self.logger.info("Database initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            return False
    
    def run(self):
        """Run the complete setup process"""
        self.logger.info("Starting Synthetic Intelligence Platform setup...")
        
        steps = [
            ("Creating virtual environment", self.create_virtualenv),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up environment", self.setup_environment),
            ("Initializing database", self.initialize_database)
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"Step: {step_name}")
            if not step_func():
                self.logger.error(f"Setup failed at: {step_name}")
                return False
        
        self.logger.info("Setup completed successfully!")
        self.logger.info("\nNext steps:")
        self.logger.info("1. Configure your .env file with API keys")
        self.logger.info("2. Activate virtual environment:")
        self.logger.info("   - Linux/Mac: source venv/bin/activate")
        self.logger.info("   - Windows: venv\\Scripts\\activate")
        self.logger.info("3. Run: python src/main.py")
        
        return True

if __name__ == '__main__':
    setup = PlatformSetup()
    success = setup.run()
    sys.exit(0 if success else 1)

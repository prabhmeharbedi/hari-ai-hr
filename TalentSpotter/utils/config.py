"""
Configuration utility functions
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration from config.json file
    
    Returns:
        dict: The configuration data
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {CONFIG_FILE}")
            return config
        else:
            # Create default configuration
            default_config = {
                'jd_summarizer': {
                    'model': 'gemma:2b'
                },
                'recruiter': {
                    'cv_analysis_model': 'phi:2.7b',
                    'matching_model': 'phi:2.7b'
                },
                'shortlister': {
                    'model': 'tinyllama:1.1b',
                    'threshold': 70
                },
                'scheduler': {
                    'model': 'flant5:small',
                    'company_name': 'AI Recruitment Solutions'
                },
                'system': {
                    'max_upload_size_mb': 10,
                    'pagination_size': 25,
                    'enable_caching': True,
                    'cache_duration_minutes': 30,
                    'enable_debug_logs': False
                },
                'notifications': {
                    'email_notifications': True,
                    'admin_email': '',
                    'notify_on_new_candidate': True,
                    'notify_on_shortlist': True,
                    'notify_on_interview': True,
                    'daily_summary': False
                }
            }
            
            # Save default configuration
            save_config(default_config)
            logger.info(f"Created default configuration in {CONFIG_FILE}")
            return default_config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        # Return minimal default configuration
        return {
            'jd_summarizer': {'model': 'gemma:2b'},
            'recruiter': {'cv_analysis_model': 'phi:2.7b', 'matching_model': 'phi:2.7b'},
            'shortlister': {'model': 'tinyllama:1.1b', 'threshold': 70},
            'scheduler': {'model': 'flant5:small', 'company_name': 'AI Recruitment Solutions'}
        }

def save_config(config):
    """
    Save configuration to config.json file
    
    Args:
        config (dict): The configuration data to save
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved configuration to {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

def get_config_value(key_path, default=None):
    """
    Get a specific configuration value using dot notation
    
    Args:
        key_path (str): Dot-separated path to config value (e.g., 'recruiter.cv_analysis_model')
        default: Default value to return if key not found
        
    Returns:
        The configuration value or the default
    """
    config = load_config()
    keys = key_path.split('.')
    
    current = config
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default
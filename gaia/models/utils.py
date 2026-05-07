import os
from datetime import datetime

class PrototypeErrorLogger:
    def __init__(self, log_file="prototype_errors.log", version="1.0"):
        self.log_file = log_file
        self.version = version
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("# GAIA.AI Prototype Error Log\n")
                f.write(f"# Version: {self.version}\n")
                f.write("# Format: [TIMESTAMP] [VERSION] [ERROR_TYPE] [FUNCTION] - MESSAGE\n\n")
    
    def log_error(self, error_type, function_name, message, severity="MEDIUM"):
        """Log an error with timestamp and version"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] [{self.version}] [{severity}] [{error_type}] [{function_name}] - {message}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(error_entry)
            print(f"Error logged: {error_entry.strip()}")
        except Exception as e:
            print(f"Failed to log error: {e}")
    
    def log_user_feedback(self, section, issue_description, user_id=None):
        """Log user feedback about issues"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = f"User:{user_id}" if user_id else "Anonymous"
        feedback_entry = f"[{timestamp}] [{self.version}] [USER_FEEDBACK] [{section}] [{user_info}] - {issue_description}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(feedback_entry)
        except Exception:
            pass

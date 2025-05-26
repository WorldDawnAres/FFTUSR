import datetime

AUTH_ENABLED = False
USERS = {}

class UiConfigManager:
    _active_sessions = {}
    max_sessions = 10
    
    def __init__(self):
        from file_transfer.tools.config import ConfigManager,CONFIG_PATH
        self.config_manager = ConfigManager(CONFIG_PATH)
        self.config = self.config_manager.config

    @classmethod
    def set_max_sessions(cls, max_sessions):
        cls.max_sessions = max_sessions
    
    @classmethod
    def add_active_session(cls, username, session_id):
        cls._active_sessions[session_id] = {
            'username': username,
            'login_time': datetime.datetime.now()
        }
    
    @classmethod
    def remove_active_session(cls, session_id):
        if session_id in cls._active_sessions:
            del cls._active_sessions[session_id]

    @classmethod
    def get_active_sessions_count(cls):
        current_time = datetime.datetime.now()
        expired_sessions = [sid for sid, session in cls._active_sessions.items() 
                          if (current_time - session['login_time']).seconds > 3600]  # 1小时超时
        for sid in expired_sessions:
            cls.remove_active_session(sid)
        return len(cls._active_sessions)

    def get_auth_enabled(self):
        return self.config.get('auth_enabled', AUTH_ENABLED)

    def set_auth_enabled(self, enabled):
        self.config['auth_enabled'] = enabled
        self.save_config()
    
    def save_config(self):
        self.config_manager.save_config()

    def get_users(self):
        return self.config.get('users', USERS)

    def add_user(self, username, password):
        users = self.get_users()
        users[username] = password
        self.config['users'] = users
        self.save_config()

    def remove_user(self, username):
        users = self.get_users()
        if username in users:
            del users[username]
            self.config['users'] = users
            self.save_config()
            return True
        return False

    @classmethod
    def get_user_session(cls, username):
        for session_id, session in cls._active_sessions.items():
            if session['username'] == username:
                return session_id, session
        return None, None

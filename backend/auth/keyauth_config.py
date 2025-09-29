"""
KeyAuth configuration and management for SECRIMPO
"""
from keyauth import api
from typing import Dict, Any, Optional
import os
from datetime import datetime

class KeyAuthManager:
    def __init__(self):
        # KeyAuth configuration - Usando suas credenciais
        self.app_name = "Secrimpo"  # Nome da aplicação
        self.owner_id = "eqVjoVksfB"  # ID da conta
        self.secret = os.getenv("KEYAUTH_SECRET", "61448643819ae5b00418dcfe9d171662a62db6d16cad37f8bc7ce57420efa1c4")
        self.version = "1.0"  # Versão da aplicação
        self.keyauth = None
        self.initialized = False
        
        # Initialize KeyAuth API only if we have valid credentials
        if self.secret != "YOUR_SECRET" and self.secret != self.owner_id:
            try:
                self.keyauth = api.Keyauth(
                    name=self.app_name,
                    owner_id=self.owner_id,
                    secret=self.secret,
                    version=self.version,
                    file_hash="" # Not needed for server apps
                )
                self.initialized = True
                print("✅ KeyAuth initialized successfully")
            except Exception as e:
                print(f"❌ KeyAuth initialization failed: {e}")
                print("⚠️  Server will start in demo mode. Please check your KeyAuth credentials.")
                self.initialized = False
        else:
            print("⚠️  KeyAuth SECRET not configured. Server starting in demo mode.")
            print("🔑 Please set your KeyAuth SECRET in the .env file to enable authentication.")
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validates a license key and returns user data"""
        if not self.initialized:
            # Demo mode - accept any license key for testing
            # Simular diferentes tipos de usuário baseado na chave
            if license_key.lower() in ["admin", "administrator", "admin-key"]:
                subscription = "admin"
                username = "admin_user"
            elif license_key.lower() in ["agent", "agente", "agent-key"]:
                subscription = "agent"
                username = "agent_user"
            elif license_key.lower() in ["viewer", "visualizador", "viewer-key"]:
                subscription = "viewer"
                username = "viewer_user"
            else:
                # Qualquer outra chave é admin por padrão
                subscription = "admin"
                username = "demo_user"
            
            return {
                "valid": True,
                "user_data": {
                    "username": username,
                    "subscription": subscription,
                    "expires": "Never",
                    "created_at": "2024-01-01",
                    "last_login": "2024-01-01"
                },
                "subscription": subscription
            }
            
        try:
            self.keyauth.license(license_key)
            
            # Extract user data from KeyAuth response
            user_data = {
                "username": self.keyauth.user_data.username,
                "subscription": self.keyauth.user_data.subscription,
                "expires": self.keyauth.user_data.subscriptions[0]["expiry"] if self.keyauth.user_data.subscriptions else None,
                "created_at": self.keyauth.user_data.createdate,
                "last_login": self.keyauth.user_data.lastlogin
            }
            
            return {
                "valid": True,
                "user_data": user_data,
                "subscription": user_data["subscription"]
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with KeyAuth credentials (username/password)."""
        if not self.initialized:
            # Demo fallback users
            demo_users = {
                "admin": {"password": "admin", "subscription": "admin"},
                "agent": {"password": "agent", "subscription": "agent"},
                "viewer": {"password": "viewer", "subscription": "viewer"},
            }
            user = demo_users.get(username)
            if user and user["password"] == password:
                user_data = {
                    "username": username,
                    "subscription": user["subscription"],
                    "expires": "Never",
                    "created_at": "2024-01-01",
                    "last_login": datetime.now().strftime("%Y-%m-%d")
                }
                return {"valid": True, "user_data": user_data}
            return {"valid": False, "error": "Invalid credentials"}

        try:
            # Use KeyAuth user login
            # The python keyauth API exposes: self.keyauth.login(user, passwd)
            self.keyauth.login(username, password)
            # Some keyauth python builds may not expose user_data; build safe defaults
            ud = getattr(self.keyauth, "user_data", None)
            if ud is not None:
                subscription = getattr(ud, "subscription", None)
                # subscriptions list can be dicts; handle safely
                subs_list = getattr(ud, "subscriptions", []) or []
                expiry = None
                if isinstance(subs_list, (list, tuple)) and subs_list:
                    first = subs_list[0]
                    if isinstance(first, dict):
                        expiry = first.get("expiry")
                user_data = {
                    "username": getattr(ud, "username", username),
                    "subscription": subscription or "agent",
                    "expires": expiry,
                    "created_at": getattr(ud, "createdate", None),
                    "last_login": getattr(ud, "lastlogin", None)
                }
            else:
                # Fallback if SDK doesn't return user_data
                user_data = {
                    "username": username,
                    "subscription": os.getenv("DEFAULT_SUBSCRIPTION", "agent"),
                    "expires": None,
                    "created_at": None,
                    "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            return {"valid": True, "user_data": user_data}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def get_user_permissions(self, subscription: str) -> Dict[str, bool]:
        """Define permissions based on subscription type"""
        permission_levels = {
            "admin": {
                "create_occurrence": True,
                "edit_occurrence": True,
                "delete_occurrence": True,
                "view_all_occurrences": True,
                "export_reports": True,
                "manage_users": True,
                "view_statistics": True,
                "system_config": True
            },
            "agent": {
                "create_occurrence": True,
                "edit_occurrence": True,
                "delete_occurrence": False,
                "view_all_occurrences": True,
                "export_reports": True,
                "manage_users": False,
                "view_statistics": True,
                "system_config": False
            },
            "viewer": {
                "create_occurrence": False,
                "edit_occurrence": False,
                "delete_occurrence": False,
                "view_all_occurrences": True,
                "export_reports": False,
                "manage_users": False,
                "view_statistics": True,
                "system_config": False
            },
            "restricted": {
                "create_occurrence": False,
                "edit_occurrence": False,
                "delete_occurrence": False,
                "view_all_occurrences": False,
                "export_reports": False,
                "manage_users": False,
                "view_statistics": False,
                "system_config": False
            }
        }
        
        return permission_levels.get(subscription.lower(), permission_levels["restricted"])
    
    def validate_and_get_permissions(self, license_key: str) -> Optional[Dict[str, Any]]:
        """Validates license and returns full user context"""
        validation_result = self.validate_license(license_key)
        
        if not validation_result["valid"]:
            return None
        
        user_data = validation_result["user_data"]
        permissions = self.get_user_permissions(user_data["subscription"])
        
        return {
            "user_data": user_data,
            "permissions": permissions,
            "subscription": user_data["subscription"],
            "username": user_data["username"]
        }
    
    def log_user_action(self, username: str, action: str, details: str = ""):
        """Log user actions for audit trail"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {username}: {action}"
        if details:
            log_entry += f" - {details}"
        
        print(f"🔍 AUDIT: {log_entry}")
        
        # TODO: Implement proper logging to file or database
        # This could be extended to log to a file or database for audit purposes

# Global instance
auth_manager = KeyAuthManager()
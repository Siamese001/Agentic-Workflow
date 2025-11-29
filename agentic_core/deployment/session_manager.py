#!/usr/bin/env python3
"""
Session Manager
Section 18: Deployment Layer - Session management for deployment
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"

@dataclass
class Session:
    """User session for deployment"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    status: SessionStatus
    data: Dict[str, Any]
    expires_at: Optional[datetime] = None

class SessionManager:
    """Manages user sessions for deployment"""
    
    def __init__(self, session_timeout_hours: int = 24):
        self.session_timeout_hours = session_timeout_hours
        self.sessions: Dict[str, Session] = {}
        self.active_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    def create_session(self, user_id: str, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """Create new user session"""
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            expires_at = now + timedelta(hours=self.session_timeout_hours)
            
            session = Session(
                session_id=session_id,
                user_id=user_id,
                created_at=now,
                last_activity=now,
                status=SessionStatus.ACTIVE,
                data=initial_data or {},
                expires_at=expires_at
            )
            
            self.sessions[session_id] = session
            self.active_sessions[user_id] = session_id
            
            logger.info(f"Session created: {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return ""
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and self._is_session_valid(session):
            return session
        return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        session = self.get_session(session_id)
        if session:
            session.data.update(data)
            session.last_activity = datetime.now()
            return True
        return False
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate session"""
        session = self.sessions.get(session_id)
        if session:
            session.status = SessionStatus.TERMINATED
            self.active_sessions.pop(session.user_id, None)
            logger.info(f"Session terminated: {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        now = datetime.now()
        expired_count = 0
        
        for session_id, session in list(self.sessions.items()):
            if session.expires_at and now > session.expires_at:
                session.status = SessionStatus.EXPIRED
                self.active_sessions.pop(session.user_id, None)
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired sessions")
        
        return expired_count
    
    def _is_session_valid(self, session: Session) -> bool:
        """Check if session is valid"""
        if session.status != SessionStatus.ACTIVE:
            return False
        
        if session.expires_at and datetime.now() > session.expires_at:
            session.status = SessionStatus.EXPIRED
            self.active_sessions.pop(session.user_id, None)
            return False
        
        return True

# Re-export components
__all__ = [
    'SessionManager', 'Session', 'SessionStatus'
]

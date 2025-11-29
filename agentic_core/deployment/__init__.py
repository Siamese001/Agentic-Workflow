#!/usr/bin/env python3
"""
Deployment Layer
Section 18: Deployment Layer - REST interface, session management
"""

from .rest_interface import RESTInterface, DeploymentConfig, HTTPMethod
from .session_manager import SessionManager, Session, SessionStatus

__all__ = [
    'RESTInterface', 'DeploymentConfig', 'HTTPMethod',
    'SessionManager', 'Session', 'SessionStatus'
]

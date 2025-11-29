"""
REST API Interface - Section 18

Provides REST interface for the agentic system with
authentication, session management, and orchestration endpoints.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, UTC
import logging
import json

try:
    from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
except ImportError:
    # Create stub classes for environments without FastAPI
    class FastAPI:
        def __init__(self, **kwargs): pass
        def add_middleware(self, middleware, **kwargs): pass
        def include_router(self, router): pass
        def get(self, path, **kwargs): return lambda f: f
        def post(self, path, **kwargs): return lambda f: f
        def put(self, path, **kwargs): return lambda f: f
        def delete(self, path, **kwargs): return lambda f: f
    
    class HTTPException(Exception): pass
    class Depends: pass
    class status: pass
    class Request: pass
    class Response: pass
    class HTTPBearer: pass
    class HTTPAuthorizationCredentials: pass
    class CORSMiddleware: pass
    class JSONResponse: pass
    class BaseModel: pass
    class Field: pass

from .auth import AuthManager, User, Session, UserRole, Permission
from .config import DeploymentConfig, Environment

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserCreateRequest(BaseModel):
    """User creation request model."""
    username: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"


class OrchestrationRequest(BaseModel):
    """Orchestration request model."""
    task_type: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None


class OrchestrationResponse(BaseModel):
    """Orchestration response model."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    environment: str
    version: str
    timestamp: datetime
    services: Dict[str, str]


class APIManager:
    """
    REST API manager for the agentic system.
    
    Provides FastAPI-based REST interface with authentication,
    session management, and orchestration endpoints.
    """
    
    def __init__(self, config: DeploymentConfig, auth_manager: AuthManager):
        """
        Initialize API manager.
        
        Args:
            config: Deployment configuration
            auth_manager: Authentication manager
        """
        self.config = config
        self.auth_manager = auth_manager
        self.app = self._create_app()
        self._setup_routes()
        self._setup_middleware()
        
        logger.info(f"Initialized API for environment: {config.environment.value}")
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""
        return FastAPI(
            title="Agentic System API",
            description="REST API for agentic workflow orchestration",
            version="1.0.0",
            debug=self.config.api.debug
        )
    
    def _setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        if self.config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.api.cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = datetime.now(UTC)
            response = await call_next(request)
            process_time = (datetime.now(UTC) - start_time).total_seconds()
            
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        # Health check endpoint
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthResponse(
                status="healthy",
                environment=self.config.environment.value,
                version="1.0.0",
                timestamp=datetime.now(UTC),
                services={
                    "api": "healthy",
                    "auth": "healthy",
                    "orchestration": "healthy"
                }
            )
        
        # Authentication endpoints
        @self.app.post("/auth/login", response_model=LoginResponse)
        async def login(request: LoginRequest):
            """User login endpoint."""
            user = self.auth_manager.authenticate_user(
                request.username, request.password
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )
            
            # Create tokens
            access_token = self.auth_manager.create_token(
                user, token_type="access"
            )
            refresh_token = self.auth_manager.create_token(
                user, token_type="refresh"
            )
            
            # Create session
            session = self.auth_manager.create_session(user)
            
            return LoginResponse(
                access_token=access_token.token_id,
                refresh_token=refresh_token.token_id,
                expires_in=self.config.security.access_token_expire_minutes * 60,
                user={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "permissions": list(user.permissions)
                }
            )
        
        @self.app.post("/auth/logout")
        async def logout(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
            """User logout endpoint."""
            token = self.auth_manager.validate_token(credentials.credentials)
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Revoke token and user sessions
            self.auth_manager.revoke_token(token.token_id)
            self.auth_manager.revoke_all_user_sessions(token.user_id)
            
            return {"message": "Logged out successfully"}
        
        @self.app.post("/auth/refresh")
        async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
            """Refresh access token endpoint."""
            token = self.auth_manager.validate_token(credentials.credentials)
            if not token or token.token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user = self.auth_manager.get_user_by_id(token.user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Create new access token
            new_access_token = self.auth_manager.create_token(
                user, token_type="access"
            )
            
            return {
                "access_token": new_access_token.token_id,
                "token_type": "bearer",
                "expires_in": self.config.security.access_token_expire_minutes * 60
            }
        
        # User management endpoints (admin only)
        @self.app.post("/admin/users")
        async def create_user(
            request: UserCreateRequest,
            current_user: User = Depends(self._get_current_user)
        ):
            """Create new user (admin only)."""
            if not current_user.has_permission(Permission.MANAGE_USERS):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            try:
                role = UserRole(request.role) if request.role else UserRole.USER
                user = self.auth_manager.create_user(
                    username=request.username,
                    email=request.email,
                    password=request.password,
                    role=role
                )
                
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "created_at": user.created_at
                }
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        @self.app.get("/admin/users")
        async def list_users(
            current_user: User = Depends(self._get_current_user)
        ):
            """List all users (admin only)."""
            if not current_user.has_permission(Permission.MANAGE_USERS):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            users = []
            for user in self.auth_manager._users.values():
                users.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "last_login": user.last_login
                })
            
            return {"users": users}
        
        # Orchestration endpoints
        @self.app.post("/orchestrate", response_model=OrchestrationResponse)
        async def orchestrate_task(
            request: OrchestrationRequest,
            current_user: User = Depends(self._get_current_user)
        ):
            """Execute orchestration task."""
            if not current_user.has_permission(Permission.EXECUTE):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            # Generate task ID
            import uuid
            task_id = str(uuid.uuid4())
            
            try:
                # Mock orchestration execution
                result = await self._execute_orchestration(
                    task_type=request.task_type,
                    parameters=request.parameters,
                    context=request.context or {},
                    user_id=current_user.id
                )
                
                return OrchestrationResponse(
                    task_id=task_id,
                    status="completed",
                    result=result,
                    created_at=datetime.now(UTC)
                )
                
            except Exception as e:
                logger.error(f"Orchestration failed for task {task_id}: {str(e)}")
                return OrchestrationResponse(
                    task_id=task_id,
                    status="failed",
                    error=str(e),
                    created_at=datetime.now(UTC)
                )
        
        @self.app.get("/orchestrate/{task_id}")
        async def get_task_status(
            task_id: str,
            current_user: User = Depends(self._get_current_user)
        ):
            """Get task status."""
            # Mock task status retrieval
            return {
                "task_id": task_id,
                "status": "completed",
                "created_at": datetime.now(UTC),
                "completed_at": datetime.now(UTC)
            }
    
    async def _execute_orchestration(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute orchestration task (mock implementation).
        
        Args:
            task_type: Type of orchestration task
            parameters: Task parameters
            context: Task context
            user_id: User ID executing the task
            
        Returns:
            Task execution result
        """
        # Mock implementation - in real system, this would call L3 orchestration
        logger.info(f"Executing orchestration task: {task_type} for user: {user_id}")
        
        if task_type == "resume_draft":
            return {
                "draft_content": "Generated resume draft content...",
                "metadata": {
                    "word_count": 150,
                    "sections": ["summary", "experience", "skills"],
                    "generated_at": datetime.now(UTC).isoformat()
                }
            }
        elif task_type == "outreach_message":
            return {
                "message_content": "Generated outreach message...",
                "metadata": {
                    "tone": "professional",
                    "length": "medium",
                    "generated_at": datetime.now(UTC).isoformat()
                }
            }
        else:
            return {
                "result": f"Executed {task_type} task",
                "parameters": parameters,
                "executed_at": datetime.now(UTC).isoformat()
            }
    
    def _get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
        """
        Get current user from authorization token.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Current authenticated user
            
        Raises:
            HTTPException: If authentication fails
        """
        if not self.config.enable_auth:
            # Return mock user for development
            return self.auth_manager.get_user_by_username("admin") or list(self.auth_manager._users.values())[0]
        
        token = self.auth_manager.validate_token(credentials.credentials)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        user = self.auth_manager.get_user_by_id(token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application instance."""
        return self.app


def create_app(config: Optional[DeploymentConfig] = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        config: Deployment configuration
        
    Returns:
        Configured FastAPI application
    """
    if config is None:
        from .config import load_config
        config = load_config()
    
    # Initialize auth manager
    auth_config = {
        "session_timeout_minutes": config.security.access_token_expire_minutes,
        "access_token_expire_minutes": config.security.access_token_expire_minutes,
        "refresh_token_expire_days": config.security.refresh_token_expire_days,
        "password_min_length": config.security.password_min_length,
    }
    auth_manager = AuthManager(auth_config)
    
    # Create API manager
    api_manager = APIManager(config, auth_manager)
    
    logger.info(f"Created FastAPI app for environment: {config.environment.value}")
    return api_manager.get_app()


# Development server runner
def run_dev_server():
    """Run development server."""
    import uvicorn
    
    config = load_config()
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug,
        log_level=config.logging.level.lower()
    )


if __name__ == "__main__":
    run_dev_server()


__all__ = [
    "APIManager",
    "create_app",
    "run_dev_server",
    "LoginRequest",
    "LoginResponse",
    "OrchestrationRequest",
    "OrchestrationResponse",
    "HealthResponse"
]






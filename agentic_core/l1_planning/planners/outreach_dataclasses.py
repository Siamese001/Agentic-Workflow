#!/usr/bin/env python3
"""
Outreach Dataclasses
Data structures for outreach planning components
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class OutreachMessage:
    """Data structure for outreach messages"""
    recipient: str
    content: str
    timestamp: str
    
@dataclass
class OutreachResearch:
    """Data structure for outreach research data"""
    company: str
    contacts: List[Dict[str, Any]]
    insights: Dict[str, Any]

@dataclass
class OutreachProfile:
    """Data structure for outreach profiles"""
    profile_id: str
    data: Dict[str, Any]
    preferences: Dict[str, Any]

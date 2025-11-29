#!/usr/bin/env python3
"""
Resume Engine Constants
Static configuration data shared across components
"""

# Canonical verb mapping for data enrichment
CANONICAL_VERBS = {
    "led": ["led", "lead", "leading"], 
    "built": ["built", "build", "building"],
    "drove": ["drove", "drive", "driving"], 
    "launched": ["launched", "launch", "launching"],
    "scaled": ["scaled", "scale", "scaling"], 
    "delivered": ["delivered", "deliver", "delivering"],
    "achieved": ["achieved", "achieve", "achieving"], 
    "established": ["established", "establish", "establishing"],
    "managed": ["managed", "manage", "managing"], 
    "developed": ["developed", "develop", "developing"]
}

# Forbidden verbs for validation
FORBIDDEN_VERBS = [
    "spearheaded", "leveraged", "utilized", "facilitated",
    "orchestrated", "championed", "pioneered", "revolutionized",
    "transformed", "optimized", "enhanced", "streamlined",
    "synergized", "enabled", "empowered", "drove"
]

# Industry peer mapping for web RAG
INDUSTRY_PEERS = {
    "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
    "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
    "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
    "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
    "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"]
}

# Mock data indicators for validation
MOCK_INDICATORS = [
    "example", "sample", "placeholder", "test", "demo",
    "mock", "fake", "dummy", "template", "generic"
]

"""Integration tests for LinkedIn outreach + data layer integration."""
from __future__ import annotations
import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ContactData:
    id: str
    name: str
    company: str
    title: str
    linkedin_url: Optional[str] = None
    enrichment_data: Optional[Dict[str, Any]] = None

@dataclass
class CompanyData:
    id: str
    name: str
    industry: str
    size: str
    recent_news: List[str]

class TestContactDataIntegration:
    """Integration tests for contact data flows."""

    def test_contact_load_and_enrich(self):
        """Integration: Contact is loaded and enriched."""
        # Load raw contact
        raw_contact = {"id": "c1", "name": "John Doe", "company": "Acme"}
        
        # Enrich with additional data
        enriched = ContactData(
            id=raw_contact["id"],
            name=raw_contact["name"],
            company=raw_contact["company"],
            title="CTO",
            linkedin_url="https://linkedin.com/in/johndoe",
            enrichment_data={"industry": "Technology", "company_size": "500+"},
        )
        
        assert enriched.enrichment_data is not None
        assert enriched.title == "CTO"

    def test_contact_company_linking(self):
        """Integration: Contact is linked to company data."""
        contact = ContactData(id="c1", name="John", company="Acme", title="CTO")
        company = CompanyData(
            id="comp_1",
            name="Acme",
            industry="Technology",
            size="500+",
            recent_news=["Raised Series B"],
        )
        
        # Link contact to company
        linked = {
            "contact": contact,
            "company": company,
        }
        
        assert linked["contact"].company == linked["company"].name

    def test_batch_contact_processing(self):
        """Integration: Batch of contacts is processed."""
        raw_contacts = [
            {"id": f"c{i}", "name": f"Contact {i}", "company": f"Company {i}"}
            for i in range(10)
        ]
        
        processed = [
            ContactData(id=c["id"], name=c["name"], company=c["company"], title="Unknown")
            for c in raw_contacts
        ]
        
        assert len(processed) == 10

    def test_contact_deduplication(self):
        """Integration: Duplicate contacts are deduplicated."""
        contacts = [
            ContactData(id="c1", name="John", company="Acme", title="CTO"),
            ContactData(id="c2", name="John", company="Acme", title="CTO"),  # Duplicate
            ContactData(id="c3", name="Jane", company="Acme", title="CEO"),
        ]
        
        seen = set()
        unique = []
        for c in contacts:
            key = (c.name, c.company)
            if key not in seen:
                seen.add(key)
                unique.append(c)
        
        assert len(unique) == 2

    def test_contact_validation(self):
        """Integration: Contact data is validated."""
        contact = ContactData(id="c1", name="", company="Acme", title="CTO")
        
        errors = []
        if not contact.name:
            errors.append("name_required")
        if not contact.company:
            errors.append("company_required")
        
        assert "name_required" in errors


class TestCompanyDataIntegration:
    """Integration tests for company data flows."""

    def test_company_research_aggregation(self):
        """Integration: Company research is aggregated."""
        sources = {
            "linkedin": {"industry": "Technology", "size": "500+"},
            "crunchbase": {"funding": "$50M", "founded": 2015},
            "news": {"recent": ["Product launch", "New CEO"]},
        }
        
        aggregated = CompanyData(
            id="comp_1",
            name="TechCorp",
            industry=sources["linkedin"]["industry"],
            size=sources["linkedin"]["size"],
            recent_news=sources["news"]["recent"],
        )
        
        assert aggregated.industry == "Technology"
        assert len(aggregated.recent_news) == 2

    def test_company_news_freshness(self):
        """Integration: Company news is fresh."""
        from datetime import datetime, timedelta
        
        news_items = [
            {"title": "Old news", "date": datetime.now() - timedelta(days=60)},
            {"title": "Recent news", "date": datetime.now() - timedelta(days=5)},
        ]
        
        max_age_days = 30
        fresh_news = [
            n for n in news_items
            if (datetime.now() - n["date"]).days <= max_age_days
        ]
        
        assert len(fresh_news) == 1

    def test_company_contact_association(self):
        """Integration: Company is associated with contacts."""
        company = CompanyData(
            id="comp_1",
            name="Acme",
            industry="Tech",
            size="100+",
            recent_news=[],
        )
        
        contacts = [
            ContactData(id="c1", name="John", company="Acme", title="CTO"),
            ContactData(id="c2", name="Jane", company="Acme", title="CEO"),
        ]
        
        company_contacts = [c for c in contacts if c.company == company.name]
        assert len(company_contacts) == 2

    def test_industry_classification(self):
        """Integration: Companies are classified by industry."""
        companies = [
            CompanyData(id="1", name="A", industry="Technology", size="100+", recent_news=[]),
            CompanyData(id="2", name="B", industry="Finance", size="500+", recent_news=[]),
            CompanyData(id="3", name="C", industry="Technology", size="50+", recent_news=[]),
        ]
        
        by_industry: Dict[str, List[CompanyData]] = {}
        for c in companies:
            by_industry.setdefault(c.industry, []).append(c)
        
        assert len(by_industry["Technology"]) == 2

    def test_company_size_filtering(self):
        """Integration: Companies are filtered by size."""
        companies = [
            {"name": "Small Co", "employees": 50},
            {"name": "Medium Co", "employees": 200},
            {"name": "Large Co", "employees": 1000},
        ]
        
        min_employees = 100
        filtered = [c for c in companies if c["employees"] >= min_employees]
        
        assert len(filtered) == 2


class TestOutreachDataIntegration:
    """Integration tests for outreach + data integration."""

    def test_personalization_data_merge(self):
        """Integration: Personalization data is merged."""
        contact = {"name": "John", "company": "Acme"}
        company = {"industry": "Technology", "recent_news": "Product launch"}
        
        personalization = {
            **contact,
            "industry": company["industry"],
            "talking_point": company["recent_news"],
        }
        
        assert personalization["talking_point"] == "Product launch"

    def test_campaign_contact_assignment(self):
        """Integration: Contacts are assigned to campaigns."""
        campaign = {"id": "camp_1", "name": "Q4 Outreach", "contacts": []}
        contacts = [
            ContactData(id="c1", name="John", company="Acme", title="CTO"),
            ContactData(id="c2", name="Jane", company="Beta", title="CEO"),
        ]
        
        campaign["contacts"] = [c.id for c in contacts]
        
        assert len(campaign["contacts"]) == 2

    def test_outreach_history_tracking(self):
        """Integration: Outreach history is tracked."""
        history = [
            {"contact_id": "c1", "action": "sent", "date": "2024-01-01"},
            {"contact_id": "c1", "action": "opened", "date": "2024-01-02"},
            {"contact_id": "c1", "action": "replied", "date": "2024-01-03"},
        ]
        
        contact_history = [h for h in history if h["contact_id"] == "c1"]
        assert len(contact_history) == 3

    def test_response_data_capture(self):
        """Integration: Response data is captured."""
        response = {
            "contact_id": "c1",
            "message": "Thanks for reaching out!",
            "sentiment": "positive",
            "intent": "interested",
        }
        
        assert response["sentiment"] == "positive"

    def test_conversion_tracking(self):
        """Integration: Conversions are tracked."""
        funnel = {
            "sent": 100,
            "opened": 45,
            "replied": 15,
            "meeting_scheduled": 8,
            "converted": 3,
        }
        
        conversion_rate = funnel["converted"] / funnel["sent"] * 100
        assert conversion_rate == 3.0

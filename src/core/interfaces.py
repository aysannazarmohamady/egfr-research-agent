from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# DOMAIN MODELS
@dataclass
class ResearchQuery:
    """Represents a research query with its components"""
    original_question: str
    keywords: List[str]
    sources: List[str]
    language: str = "en"

class SearchResultType(Enum):
    CASE_REPORT = "case_report"
    CLINICAL_STUDY = "clinical_study"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    OTHER = "other"

@dataclass
class SearchResult:
    """Represents a single search result"""
    title: str
    authors: List[str]
    journal: str
    publication_date: str
    doi: Optional[str]
    pmid: Optional[str]
    url: str
    abstract: str
    result_type: SearchResultType
    relevance_score: float

@dataclass
class ResearchReport:
    """Final research report"""
    query: ResearchQuery
    total_papers_found: int
    relevant_papers: List[SearchResult]
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    evidence_level: str

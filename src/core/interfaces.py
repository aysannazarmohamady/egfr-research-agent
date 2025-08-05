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

# CORE INTERFACES
class IKeywordExtractor(ABC):
    """Interface for keyword extraction strategies"""
    
    @abstractmethod
    def extract_keywords(self, question: str) -> List[str]:
        pass

class ISourceRecommender(ABC):
    """Interface for source recommendation strategies"""
    
    @abstractmethod
    def recommend_sources(self, keywords: List[str]) -> List[str]:
        pass

class ISearchEngine(ABC):
    """Interface for different search engines"""
    
    @abstractmethod
    def search(self, keywords: List[str], source: str, limit: int = 50) -> List[SearchResult]:
        pass

class IContentAnalyzer(ABC):
    """Interface for content analysis strategies"""
    
    @abstractmethod
    def analyze_relevance(self, result: SearchResult, query: ResearchQuery) -> float:
        pass
    
    @abstractmethod
    def classify_paper_type(self, result: SearchResult) -> SearchResultType:
        pass

class IReportGenerator(ABC):
    """Interface for report generation strategies"""
    
    @abstractmethod
    def generate_report(self, query: ResearchQuery, results: List[SearchResult]) -> ResearchReport:
        pass

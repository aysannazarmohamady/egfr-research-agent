from typing import List
from .interfaces import (
    IKeywordExtractor, ISourceRecommender, ISearchEngine, 
    IContentAnalyzer, IReportGenerator,
    SearchResult, SearchResultType, ResearchQuery, ResearchReport
)

class SimpleKeywordExtractor(IKeywordExtractor):
    """Simple keyword extractor for testing"""
    
    def extract_keywords(self, question: str) -> List[str]:
        
        medical_keywords = [
            "osimertinib", "EGFR inhibitor", "glomerulonephritis", 
            "acute", "kidney", "nephrotoxicity", "renal"
        ]
        
        found_keywords = []
        question_lower = question.lower()
        
        for keyword in medical_keywords:
            if keyword.lower() in question_lower:
                found_keywords.append(keyword)
        
        
        if not found_keywords:
            found_keywords = ["EGFR inhibitor", "glomerulonephritis"]
            
        return found_keywords

class SimpleSourceRecommender(ISourceRecommender):
    """Simple source recommender for testing"""
    
    def recommend_sources(self, keywords: List[str]) -> List[str]:
        
        return ["PubMed", "Google Scholar"]

class MockSearchEngine(ISearchEngine):
    """Mock search engine for testing"""
    
    def search(self, keywords: List[str], source: str, limit: int = 50) -> List[SearchResult]:
        
        mock_results = [
            SearchResult(
                title=f"Osimertinib-induced acute glomerulonephritis: A case report",
                authors=["Smith J", "Doe A"],
                journal="Nephrology Case Reports",
                publication_date="2024-01-15",
                doi="10.1000/example1",
                pmid="12345678",
                url="https://example.com/paper1",
                abstract="A 65-year-old patient developed acute glomerulonephritis after osimertinib treatment...",
                result_type=SearchResultType.CASE_REPORT,
                relevance_score=0.9
            ),
            SearchResult(
                title=f"EGFR inhibitors and renal complications: systematic review",
                authors=["Johnson B", "Wilson C"],
                journal="Clinical Oncology",
                publication_date="2023-12-10",
                doi="10.1000/example2",
                pmid="87654321",
                url="https://example.com/paper2",
                abstract="Systematic review of renal complications associated with EGFR inhibitor therapy...",
                result_type=SearchResultType.SYSTEMATIC_REVIEW,
                relevance_score=0.8
            )
        ]
        
        return mock_results[:limit]

class SimpleContentAnalyzer(IContentAnalyzer):
    """Simple content analyzer for testing"""
    
    def analyze_relevance(self, result: SearchResult, query: ResearchQuery) -> float:
        score = 0.0
        title_lower = result.title.lower()
        abstract_lower = result.abstract.lower()
        
        for keyword in query.keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower:
                score += 0.3
            if keyword_lower in abstract_lower:
                score += 0.2
                
        return min(score, 1.0)
    
    def classify_paper_type(self, result: SearchResult) -> SearchResultType:
        title_lower = result.title.lower()
        
        if "case report" in title_lower:
            return SearchResultType.CASE_REPORT
        elif "systematic review" in title_lower:
            return SearchResultType.SYSTEMATIC_REVIEW
        elif "meta-analysis" in title_lower:
            return SearchResultType.META_ANALYSIS
        elif "clinical trial" in title_lower:
            return SearchResultType.CLINICAL_STUDY
        else:
            return SearchResultType.OTHER


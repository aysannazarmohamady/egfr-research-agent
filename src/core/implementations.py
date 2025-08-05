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

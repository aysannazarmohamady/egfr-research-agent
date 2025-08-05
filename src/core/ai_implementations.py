import requests
import json
import os
from typing import List
from .interfaces import IKeywordExtractor, ISourceRecommender

class GeminiKeywordExtractor(IKeywordExtractor):
    """AI-powered keyword extractor using Gemini API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    def extract_keywords(self, question: str) -> List[str]:
        """Extract keywords using Gemini AI"""
        
        prompt = f"""
You are a medical research expert. Analyze this research question and extract the most effective keywords for searching medical databases like PubMed.

Research Question: "{question}"

Instructions:
1. Extract 5-8 specific medical keywords that would be most effective for database searching
2. Include drug names, medical conditions, and relevant medical terms
3. Use exact medical terminology (e.g., "glomerulonephritis" not "kidney disease")
4. Include both generic and specific terms when relevant
5. Consider synonyms and alternative terms

Return ONLY a comma-separated list of keywords, nothing else.

Example format: osimertinib, EGFR inhibitor, acute glomerulonephritis, nephrotoxicity, renal adverse effects
"""
        
        try:
            response = self._call_gemini_api(prompt)
            keywords_text = response.strip()
            
            # Parse comma-separated keywords
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Fallback if AI fails
            if not keywords:
                return self._fallback_keywords(question)
                
            return keywords
            
        except Exception as e:
            print(f"AI keyword extraction failed: {e}")
            return self._fallback_keywords(question)
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API"""
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'candidates' not in result or not result['candidates']:
            raise Exception("No response from AI")
        
        return result['candidates'][0]['content']['parts'][0]['text']
    
    def _fallback_keywords(self, question: str) -> List[str]:
        """Fallback keyword extraction if AI fails"""
        medical_keywords = [
            "osimertinib", "EGFR inhibitor", "glomerulonephritis", 
            "acute", "nephrotoxicity", "renal", "kidney"
        ]
        
        found_keywords = []
        question_lower = question.lower()
        
        for keyword in medical_keywords:
            if keyword.lower() in question_lower:
                found_keywords.append(keyword)
        
        if not found_keywords:
            found_keywords = ["EGFR inhibitor", "glomerulonephritis"]
            
        return found_keywords

class GeminiSourceRecommender(ISourceRecommender):
    """AI-powered source recommender using Gemini API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def recommend_sources(self, keywords: List[str]) -> List[str]:
        """Recommend sources using Gemini AI"""
        
        keywords_text = ", ".join(keywords)
        
        prompt = f"""
You are a medical research librarian. Based on these keywords, recommend the best 3-4 medical databases to search for research papers.

Keywords: {keywords_text}

Available databases:
- PubMed (MEDLINE) - Primary medical literature
- Embase - European medical database
- Cochrane Library - Systematic reviews and clinical trials
- Google Scholar - Broad academic search
- Web of Science - Citation database
- CINAHL - Nursing and allied health
- Scopus - Scientific literature database

Instructions:
1. Choose 3-4 most relevant databases for these specific keywords
2. Prioritize databases that would have the most relevant papers
3. Consider the medical domain (oncology, nephrology, pharmacology)

Return ONLY a comma-separated list of database names, nothing else.

Example format: PubMed, Embase, Cochrane Library
"""
        
        try:
            response = self._call_gemini_api(prompt)
            sources_text = response.strip()
            
            # Parse comma-separated sources
            sources = [s.strip() for s in sources_text.split(',') if s.strip()]
            
            # Fallback if AI fails
            if not sources:
                return ["PubMed", "Google Scholar"]
                
            return sources
            
        except Exception as e:
            print(f"AI source recommendation failed: {e}")
            return ["PubMed", "Google Scholar", "Embase"]
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API (same as in KeywordExtractor)"""
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'candidates' not in result or not result['candidates']:
            raise Exception("No response from AI")
        
        return result['candidates'][0]['content']['parts'][0]['text']

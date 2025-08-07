import requests
import json
import re
import os
from typing import List, Optional
from .interfaces import ISearchEngine, SearchResult, SearchResultType
from datetime import datetime

class GeminiNativeSearchEngine(ISearchEngine):
    """Native search using Gemini's built-in web search capabilities"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for native search")
    
    def search(self, keywords: List[str], source: str, limit: int = 50) -> List[SearchResult]:
        """Search using Gemini's native web search"""
        
        if source.lower() not in ["google scholar", "pubmed", "academic search"]:
            return []
        
        try:
            # Build AI search prompt
            search_prompt = self._build_search_prompt(keywords, source, limit)
            print(f"🤖 Gemini Search Query for {source}")
            
            # Execute search via Gemini
            ai_response = self._call_gemini_search(search_prompt)
            print(f"📄 Raw AI response length: {len(ai_response)} chars")
            
            # Parse AI response into SearchResult objects
            results = self._parse_ai_response(ai_response, source)
            print(f"🔄 Parsed {len(results)} papers")
            
            return results[:limit]
            
        except Exception as e:
            print(f"❌ Gemini native search error: {e}")
            return []
    
    def _build_search_prompt(self, keywords: List[str], source: str, limit: int) -> str:
        """Build optimized search prompt for Gemini"""
        
        keywords_str = ", ".join(keywords)
        current_year = datetime.now().year
        
        if source.lower() == "pubmed":
            prompt = f"""
Search PubMed and medical databases for research papers about: {keywords_str}

Requirements:
- Focus on papers from {current_year-3}-{current_year} (recent 3 years)
- Find exactly {min(limit, 20)} most relevant papers
- Include case reports, clinical studies, systematic reviews
- Prioritize papers with EGFR inhibitor nephrotoxicity focus

For each paper, provide this EXACT format:
PAPER_START
Title: [exact paper title]
Authors: [author1, author2, author3]
Journal: [journal name]
Year: [publication year]
PMID: [PubMed ID if available]
DOI: [DOI if available]
URL: [direct link]
Abstract: [brief abstract or summary]
Type: [case_report/clinical_study/systematic_review/meta_analysis/other]
PAPER_END

Search now and provide real, current papers in the exact format above.
"""
        
        elif source.lower() == "google scholar":
            prompt = f"""
Search Google Scholar for academic papers about: {keywords_str}

Requirements:
- Recent papers ({current_year-3}-{current_year})
- Find exactly {min(limit, 15)} most relevant papers
- Focus on peer-reviewed medical literature
- Include nephrology and oncology journals

For each paper, provide this EXACT format:
PAPER_START
Title: [exact paper title]
Authors: [author1, author2, author3]
Journal: [journal name]
Year: [publication year]
PMID: [PubMed ID if available]  
DOI: [DOI if available]
URL: [Google Scholar or journal URL]
Abstract: [brief abstract or summary]
Type: [case_report/clinical_study/systematic_review/meta_analysis/other]
PAPER_END

Search now and provide real papers in the exact format above.
"""
        
        else:
            # Generic academic search
            prompt = f"""
Search academic databases for papers about: {keywords_str}

Find {min(limit, 15)} most relevant recent papers (2020-{current_year}) and provide in this EXACT format:

PAPER_START
Title: [exact paper title]
Authors: [author names]
Journal: [journal name]
Year: [year]
PMID: [if available]
DOI: [if available]
URL: [link]
Abstract: [summary]
Type: [paper type]
PAPER_END

Search now and provide real papers.
"""
        
        return prompt
    
    def _call_gemini_search(self, prompt: str) -> str:
        """Execute search via Gemini API"""
        
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
            ],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for factual accuracy
                "maxOutputTokens": 4000  # Allow longer responses
            }
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=data,
            timeout=60  # Longer timeout for search
        )
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if 'candidates' not in result or not result['candidates']:
            raise Exception("No response from Gemini search")
        
        return result['candidates'][0]['content']['parts'][0]['text']
    
    def _parse_ai_response(self, ai_response: str, source: str) -> List[SearchResult]:
        """Parse Gemini's search response into SearchResult objects"""
        
        results = []
        
        # Split by PAPER_START/PAPER_END markers
        paper_blocks = re.split(r'PAPER_START.*?PAPER_END', ai_response, flags=re.DOTALL)
        
        # Alternative: find papers between markers
        paper_pattern = r'PAPER_START(.*?)PAPER_END'
        paper_matches = re.findall(paper_pattern, ai_response, re.DOTALL)
        
        if not paper_matches:
            # Fallback: try to parse without markers
            paper_matches = self._fallback_parse(ai_response)
        
        for paper_text in paper_matches:
            try:
                paper = self._parse_single_paper(paper_text.strip(), source)
                if paper:
                    results.append(paper)
            except Exception as e:
                print(f"⚠️ Error parsing paper: {e}")
                continue
        
        return results
    
    def _parse_single_paper(self, paper_text: str, source: str) -> Optional[SearchResult]:
        """Parse a single paper from AI response"""
        
        try:
            # Extract fields using regex
            fields = {}
            
            patterns = {
                'title': r'Title:\s*(.+?)(?=\n|$)',
                'authors': r'Authors:\s*(.+?)(?=\n|$)', 
                'journal': r'Journal:\s*(.+?)(?=\n|$)',
                'year': r'Year:\s*(.+?)(?=\n|$)',
                'pmid': r'PMID:\s*(.+?)(?=\n|$)',
                'doi': r'DOI:\s*(.+?)(?=\n|$)',
                'url': r'URL:\s*(.+?)(?=\n|$)',
                'abstract': r'Abstract:\s*(.+?)(?=\nType:|$)',
                'type': r'Type:\s*(.+?)(?=\n|$)'
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, paper_text, re.IGNORECASE | re.DOTALL)
                fields[field] = match.group(1).strip() if match else ""
            
            # Clean and validate
            title = fields['title'].replace('[', '').replace(']', '').strip()
            if not title or len(title) < 10:
                return None
            
            # Parse authors
            authors_str = fields['authors'].replace('[', '').replace(']', '')
            authors = [a.strip() for a in authors_str.split(',') if a.strip()]
            if not authors:
                authors = ["Unknown Author"]
            
            # Clean URLs
            url = fields['url'].replace('[', '').replace(']', '').strip()
            if not url.startswith('http'):
                url = f"https://pubmed.ncbi.nlm.nih.gov/{fields['pmid']}/" if fields['pmid'] else ""
            
            # Map paper type
            paper_type = self._map_paper_type(fields['type'])
            
            return SearchResult(
                title=title,
                authors=authors[:5],  # Limit to 5 authors
                journal=fields['journal'].replace('[', '').replace(']', '').strip() or "Unknown Journal",
                publication_date=fields['year'].replace('[', '').replace(']', '').strip() or "Unknown",
                doi=fields['doi'].replace('[', '').replace(']', '').strip() or None,
                pmid=fields['pmid'].replace('[', '').replace(']', '').strip() or None,
                url=url,
                abstract=fields['abstract'][:500],  # Limit abstract length
                result_type=paper_type,
                relevance_score=0.8  # High relevance since AI filtered
            )
            
        except Exception as e:
            print(f"⚠️ Error parsing single paper: {e}")
            return None
    
    def _map_paper_type(self, type_str: str) -> SearchResultType:
        """Map AI response type to SearchResultType enum"""
        
        type_lower = type_str.lower()
        
        if 'case_report' in type_lower or 'case report' in type_lower:
            return SearchResultType.CASE_REPORT
        elif 'systematic_review' in type_lower or 'systematic review' in type_lower:
            return SearchResultType.SYSTEMATIC_REVIEW
        elif 'meta_analysis' in type_lower or 'meta-analysis' in type_lower:
            return SearchResultType.META_ANALYSIS
        elif 'clinical_study' in type_lower or 'clinical study' in type_lower:
            return SearchResultType.CLINICAL_STUDY
        else:
            return SearchResultType.OTHER
    
    def _fallback_parse(self, text: str) -> List[str]:
        """Fallback parsing when markers aren't found"""
        
        # Look for paper-like patterns
        paper_patterns = [
            r'Title:.*?(?=Title:|$)',
            r'\d+\.\s*[A-Z].*?(?=\d+\.\s*[A-Z]|$)',
        ]
        
        for pattern in paper_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches and len(matches) > 1:
                return matches
        
        # Final fallback: split by numbers
        sections = re.split(r'\n\d+\.', text)
        return [s.strip() for s in sections if len(s.strip()) > 100]

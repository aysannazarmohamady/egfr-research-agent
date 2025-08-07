import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Optional
from .interfaces import ISearchEngine, SearchResult, SearchResultType
from .ai_implementations import GeminiKeywordExtractor
import os

class GoogleScholarScraper(ISearchEngine):
    """Google Scholar web scraper with AI relevance filtering"""
    
    def __init__(self):
        self.base_url = "https://www.google.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Initialize AI relevance checker
        try:
            self.ai_checker = GeminiKeywordExtractor()
            self.ai_enabled = True
        except:
            self.ai_enabled = False
            print("AI relevance checker not available")
    
    def search(self, keywords: List[str], source: str, limit: int = 50) -> List[SearchResult]:
        """Search Google Scholar with site-specific strategy"""
        
        if source.lower() != "google scholar":
            return []
        
        try:
            # Build site-specific query
            query = self._build_scholar_query(keywords)
            print(f"Google Scholar Query: {query}")
            
            # Scrape search results
            raw_results = self._scrape_search_results(query, limit)
            print(f"Scraped {len(raw_results)} raw results")
            
            # Convert to SearchResult objects
            search_results = self._convert_to_search_results(raw_results)
            print(f"Converted {len(search_results)} results")
            
            # AI relevance filtering
            if self.ai_enabled:
                relevant_results = self._filter_relevant_papers(search_results, keywords)
                print(f"AI filtered to {len(relevant_results)} relevant papers")
                return relevant_results
            else:
                return search_results
                
        except Exception as e:
            print(f"Google Scholar scraping error: {e}")
            return []
    
    def _build_scholar_query(self, keywords: List[str]) -> str:
        """Build Google Scholar specific query"""
        
        # Create quoted phrases for important keywords
        important_terms = []
        for keyword in keywords:
            if any(term in keyword.lower() for term in ['egfr', 'osimertinib', 'erlotinib', 'nephrotoxicity', 'glomerulonephritis']):
                important_terms.append(f'"{keyword}"')
        
        # Combine with site restriction
        if important_terms:
            query = f"{' '.join(important_terms)} site:scholar.google.com"
        else:
            # Fallback: use all keywords
            all_terms = [f'"{kw}"' for kw in keywords[:3]]  # Limit to avoid too long query
            query = f"{' '.join(all_terms)} site:scholar.google.com"
        
        return query
    
    def _scrape_search_results(self, query: str, limit: int) -> List[dict]:
        """Scrape Google search results"""
        
        results = []
        num_pages = min(3, (limit // 10) + 1)  # Max 3 pages
        
        for page in range(num_pages):
            try:
                # Build URL
                params = {
                    'q': query,
                    'start': page * 10,
                    'num': 10
                }
                
                # Random delay to avoid blocking
                time.sleep(random.uniform(1, 3))
                
                # Make request
                response = requests.get(self.base_url, params=params, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract results from this page
                page_results = self._parse_search_page(soup)
                results.extend(page_results)
                
                print(f"📄 Page {page + 1}: {len(page_results)} results")
                
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error scraping page {page + 1}: {e}")
                break
        
        return results[:limit]
    
    def _parse_search_page(self, soup: BeautifulSoup) -> List[dict]:
        """Parse individual search results from page"""
        
        results = []
        
        # Find result containers
        result_containers = soup.find_all('div', class_='tF2Cxc')
        
        for container in result_containers:
            try:
                result = self._parse_single_result(container)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error parsing result: {e}")
                continue
        
        return results
    
    def _parse_single_result(self, container) -> Optional[dict]:
        """Parse a single search result"""
        
        try:
            # Extract title
            title_elem = container.find('h3', class_='LC20lb')
            if not title_elem:
                return None
            title = title_elem.get_text().strip()
            
            # Extract URL
            link_elem = container.find('a')
            if not link_elem:
                return None
            url = link_elem.get('href', '')
            
            # Extract snippet/description
            snippet_elem = container.find('div', class_='VwiC3b')
            snippet = snippet_elem.get_text().strip() if snippet_elem else ""
            
            # Extract citation info if available
            cite_elem = container.find('cite')
            domain = cite_elem.get_text().strip() if cite_elem else ""
            
            return {
                'title': title,
                'url': url,
                'snippet': snippet,
                'domain': domain,
                'authors': [],  # Will be extracted from snippet if possible
                'year': self._extract_year_from_snippet(snippet)
            }
            
        except Exception as e:
            print(f"Error parsing single result: {e}")
            return None
    
    def _extract_year_from_snippet(self, snippet: str) -> str:
        """Extract publication year from snippet"""
        import re
        
        # Look for 4-digit years between 2000-2024
        year_match = re.search(r'\b(20[0-2][0-9])\b', snippet)
        return year_match.group(1) if year_match else "Unknown"
    
    def _convert_to_search_results(self, raw_results: List[dict]) -> List[SearchResult]:
        """Convert raw scraped data to SearchResult objects"""
        
        search_results = []
        
        for raw in raw_results:
            try:
                # Extract authors from snippet if possible
                authors = self._extract_authors_from_snippet(raw['snippet'])
                
                result = SearchResult(
                    title=raw['title'],
                    authors=authors,
                    journal="Google Scholar",  # Generic
                    publication_date=raw['year'],
                    doi=None,
                    pmid=None,
                    url=raw['url'],
                    abstract=raw['snippet'][:500],  # First 500 chars as abstract
                    result_type=SearchResultType.OTHER,
                    relevance_score=0.0  # Will be calculated by AI
                )
                
                search_results.append(result)
                
            except Exception as e:
                print(f"Error converting result: {e}")
                continue
        
        return search_results
    
    def _extract_authors_from_snippet(self, snippet: str) -> List[str]:
        """Try to extract author names from snippet"""
        
        # Simple heuristic: look for patterns like "Author A, Author B"
        import re
        
        # Look for author patterns (very basic)
        author_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+(?:, [A-Z][a-z]+ [A-Z][a-z]+)*)',
            r'([A-Z]\. [A-Z][a-z]+(?:, [A-Z]\. [A-Z][a-z]+)*)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, snippet)
            if match:
                authors_str = match.group(1)
                return [author.strip() for author in authors_str.split(',')]
        
        return ["Unknown Author"]
    
    def _filter_relevant_papers(self, results: List[SearchResult], keywords: List[str]) -> List[SearchResult]:
        """Use AI to filter relevant papers"""
        
        if not self.ai_enabled:
            return results
        
        relevant_results = []
        
        for result in results:
            try:
                # Use AI to check relevance
                is_relevant, score = self._check_relevance_with_ai(result, keywords)
                
                if is_relevant:
                    result.relevance_score = score
                    relevant_results.append(result)
                
                # Small delay to avoid API rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error checking relevance: {e}")
                # If AI fails, include the paper anyway
                result.relevance_score = 0.5
                relevant_results.append(result)
        
        # Sort by relevance score
        relevant_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return relevant_results
    
    def _check_relevance_with_ai(self, result: SearchResult, keywords: List[str]) -> tuple[bool, float]:
        """Use AI to check if paper is relevant"""
        
        prompt = f"""
You are a medical research expert. Analyze this paper and determine if it's relevant to research on EGFR inhibitor nephrotoxicity.

Paper Title: {result.title}
Abstract/Snippet: {result.abstract}
Target Keywords: {', '.join(keywords)}

Analysis Instructions:
1. Is this paper about EGFR inhibitors (osimertinib, erlotinib, gefitinib, etc.) AND kidney/renal toxicity?
2. Or is it about targeted cancer therapy nephrotoxicity?
3. Rate the relevance from 0-100

Respond in this exact format:
RELEVANT: YES/NO
SCORE: [0-100]
REASON: [brief explanation]
"""
        
        try:
            # Use the AI checker (reusing GeminiKeywordExtractor's API method)
            response = self.ai_checker._call_gemini_api(prompt)
            
            # Parse response
            is_relevant = "YES" in response.upper()
            
            # Extract score
            import re
            score_match = re.search(r'SCORE:\s*(\d+)', response)
            score = int(score_match.group(1)) / 100.0 if score_match else 0.5
            
            return is_relevant, score
            
        except Exception as e:
            print(f"AI relevance check failed: {e}")
            return True, 0.5  # Default to include if AI fails

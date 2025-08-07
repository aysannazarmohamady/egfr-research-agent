import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from .interfaces import ISearchEngine, SearchResult, SearchResultType
import time

class PubMedSearchEngine(ISearchEngine):
    """Real PubMed search implementation using NCBI E-utilities API"""
    
    def __init__(self):
        self.base_search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.base_summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    def search(self, keywords: List[str], source: str, limit: int = 50) -> List[SearchResult]:
        """Search PubMed for papers"""
        
        # Only handle PubMed searches
        if source.lower() != "pubmed":
            return []
        
        try:
            # Step 1: Build search query
            query = self._build_search_query(keywords)
            print(f"🔍 PubMed Query: {query}")
            
            # Step 2: Search for paper IDs
            paper_ids = self._search_paper_ids(query, limit)
            print(f"📊 Found {len(paper_ids)} paper IDs")
            
            if not paper_ids:
                return []
            
            # Step 3: Get paper details
            results = self._fetch_paper_details(paper_ids)
            print(f"📄 Retrieved {len(results)} paper details")
            
            return results
            
        except Exception as e:
            print(f"❌ PubMed search error: {e}")
            return []
    
    def _build_search_query(self, keywords: List[str]) -> str:
        """Build PubMed search query using winning strategy from tests"""
        
        # Categorize keywords based on test results
        drug_terms = []
        condition_terms = []
        general_terms = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # EGFR inhibitor drugs
            if any(drug in keyword_lower for drug in ['osimertinib', 'erlotinib', 'gefitinib', 'egfr inhibitor', 'tyrosine kinase']):
                drug_terms.append(f'"{keyword}"[Title/Abstract]')
            # Kidney/renal conditions  
            elif any(condition in keyword_lower for condition in ['nephrotoxicity', 'glomerulonephritis', 'renal', 'kidney']):
                condition_terms.append(f'"{keyword}"[Title/Abstract]')
            # General terms
            else:
                general_terms.append(f'"{keyword}"[Title/Abstract]')
        
        # Build query using winning strategies
        query_parts = []
        
        # Strategy 1: Drug terms with OR (winner strategy)
        if drug_terms:
            query_parts.append("(" + " OR ".join(drug_terms) + ")")
        
        # Strategy 2: Condition terms with OR
        if condition_terms:
            query_parts.append("(" + " OR ".join(condition_terms) + ")")
        
        # Strategy 3: General terms with OR
        if general_terms:
            query_parts.append("(" + " OR ".join(general_terms) + ")")
        
        # Combine with AND (each category must have at least one match)
        if len(query_parts) > 1:
            query = " AND ".join(query_parts)
        elif query_parts:
            query = query_parts[0]
        else:
            # Fallback: simple OR of all terms
            all_terms = [f'"{kw}"[Title/Abstract]' for kw in keywords]
            query = "(" + " OR ".join(all_terms) + ")"
        
        # Add publication date filter (last 10 years)
        query += " AND 2014:2024[pdat]"
        
        return query
    
    def _search_paper_ids(self, query: str, limit: int) -> List[str]:
        """Search for paper IDs using esearch"""
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'xml',
            'sort': 'relevance'
        }
        
        response = requests.get(self.base_search_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        id_list = root.find('IdList')
        
        if id_list is None:
            return []
        
        return [id_elem.text for id_elem in id_list.findall('Id')]
    
    def _fetch_paper_details(self, paper_ids: List[str]) -> List[SearchResult]:
        """Fetch detailed information for papers"""
        
        results = []
        
        # Process in batches to avoid API limits
        batch_size = 20
        for i in range(0, len(paper_ids), batch_size):
            batch_ids = paper_ids[i:i + batch_size]
            batch_results = self._fetch_batch_details(batch_ids)
            results.extend(batch_results)
            
            # Rate limiting
            time.sleep(0.5)
        
        return results
    
    def _fetch_batch_details(self, paper_ids: List[str]) -> List[SearchResult]:
        """Fetch details for a batch of papers"""
        
        ids_str = ",".join(paper_ids)
        
        # Get paper summaries
        params = {
            'db': 'pubmed',
            'id': ids_str,
            'retmode': 'xml'
        }
        
        response = requests.get(self.base_summary_url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        results = []
        
        for doc_sum in root.findall('DocumentSummary'):
            try:
                result = self._parse_document_summary(doc_sum)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"⚠️ Error parsing document: {e}")
                continue
        
        return results
    
    def _parse_document_summary(self, doc_sum) -> Optional[SearchResult]:
        """Parse a single document summary"""
        
        try:
            # Extract basic info
            pmid = doc_sum.get('uid', '')
            title = self._get_text_content(doc_sum, 'Title', 'Unknown Title')
            
            # Extract authors
            authors = []
            author_list = doc_sum.find('AuthorList')
            if author_list is not None:
                for author in author_list.findall('Author')[:3]:  # First 3 authors
                    name = author.get('Name', '')
                    if name:
                        authors.append(name)
            
            if not authors:
                authors = ['Unknown Author']
            
            # Extract journal and date
            journal = self._get_text_content(doc_sum, 'FullJournalName', 'Unknown Journal')
            pub_date = self._get_text_content(doc_sum, 'PubDate', 'Unknown Date')
            
            # Generate DOI URL (may not always exist)
            doi = None
            article_ids = doc_sum.find('ArticleIds')
            if article_ids is not None:
                for article_id in article_ids.findall('ArticleId'):
                    if article_id.get('IdType') == 'doi':
                        doi = article_id.text
                        break
            
            # Build URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            # Get abstract (this would require additional API call)
            # For now, use title as abstract placeholder
            abstract = title
            
            return SearchResult(
                title=title,
                authors=authors,
                journal=journal,
                publication_date=pub_date,
                doi=doi,
                pmid=pmid,
                url=url,
                abstract=abstract,
                result_type=SearchResultType.OTHER,  # Will be classified later
                relevance_score=0.0  # Will be calculated later
            )
            
        except Exception as e:
            print(f"⚠️ Error parsing document summary: {e}")
            return None
    
    def _get_text_content(self, element, tag: str, default: str) -> str:
        """Safely extract text content from XML element"""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

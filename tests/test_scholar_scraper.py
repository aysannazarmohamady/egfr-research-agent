import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from core.scholar_scraper import GoogleScholarScraper

def test_scholar_scraper():
    """Test Google Scholar scraper standalone"""
    
    print("Testing Google Scholar Scraper")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Initialize scraper
    scraper = GoogleScholarScraper()
    
    # Test keywords
    test_keywords = ["EGFR inhibitor", "nephrotoxicity", "osimertinib"]
    
    print(f"🔍 Testing with keywords: {test_keywords}")
    print(f"🤖 AI enabled: {scraper.ai_enabled}")
    
    try:
        # Run search
        results = scraper.search(test_keywords, "Google Scholar", limit=5)
        
        print(f"\n RESULTS: {len(results)} papers found")
        print("=" * 50)
        
        # Display results
        for i, paper in enumerate(results, 1):
            print(f"\n Paper {i}:")
            print(f"   Title: {paper.title}")
            print(f"   Authors: {', '.join(paper.authors)}")
            print(f"   Year: {paper.publication_date}")
            print(f"   URL: {paper.url}")
            print(f"   Abstract: {paper.abstract[:100]}...")
            print(f"   Relevance: {paper.relevance_score:.2f}")
        
        if results:
            print(f"\n SUCCESS: Scholar scraper is working!")
            print(f" Found {len([r for r in results if r.relevance_score > 0.6])} highly relevant papers")
        else:
            print("\n  No results found - may need to adjust query strategy")
            
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scholar_scraper()

# Test Gemini built-in search capabilities
import requests
import os

def test_gemini_search():
    """Test if Gemini can search the web directly"""
    
    api_key = "AIzaSyBtk10-bZH3HiSmYvZu-5L-LqQvppd83eE"
    
    # Different Gemini endpoints to test
    endpoints = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    ]
    
    # Search-focused prompts
    test_prompts = [
        # Direct search request
        """Search the web for recent papers about EGFR inhibitor nephrotoxicity and provide:
1. Paper titles
2. Authors  
3. Publication years
4. Brief abstracts
5. DOI or PubMed links

Focus on papers from 2020-2024.""",

        # Alternative approach
        """Find me the latest research papers on osimertinib kidney toxicity. 
I need actual paper citations with:
- Exact titles
- Author names
- Journal names
- Publication dates
- Links/DOIs

Please search academic databases.""",

        # Tool-use approach
        """I need you to search for scientific papers about "EGFR inhibitor glomerulonephritis". 
Can you use web search tools to find:
- PubMed papers
- Google Scholar results
- Recent publications (2022-2024)
- Case reports and clinical studies

Return structured results with metadata."""
    ]
    
    print("🔍 Testing Gemini Search Capabilities")
    print("=" * 60)
    
    for endpoint in endpoints:
        model_name = "gemini-2.0-flash" if "2.0" in endpoint else "gemini-pro"
        print(f"\n🤖 Testing {model_name}")
        print("-" * 40)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: Search Request")
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': api_key
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
            
            try:
                response = requests.post(endpoint, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'candidates' in result:
                        content = result['candidates'][0]['content']['parts'][0]['text']
                        
                        # Check for search capabilities
                        indicators = [
                            "I cannot search the web",
                            "I don't have access to real-time",
                            "I cannot browse the internet", 
                            "search tools",
                            "web search",
                            "PMID:",
                            "DOI:",
                            "pubmed.ncbi.nlm.nih.gov",
                            "scholar.google.com"
                        ]
                        
                        found_indicators = [ind for ind in indicators if ind.lower() in content.lower()]
                        
                        print(f"   📊 Response length: {len(content)} chars")
                        print(f"   🔍 Search indicators: {found_indicators}")
                        
                        # Show first 200 chars
                        print(f"   📄 Preview: {content[:200]}...")
                        
                        # Check if it looks like real search results
                        if any(word in content.lower() for word in ["pmid", "doi", "pubmed", "journal"]):
                            print("   🎯 POSSIBLE SEARCH RESULTS FOUND!")
                        elif any(word in content.lower() for word in ["cannot search", "don't have access"]):
                            print("   ❌ No search capability")
                        else:
                            print("   ⚠️  Unclear - need manual review")
                            
                    else:
                        print("   ❌ No candidates in response")
                        
                else:
                    print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
            # Don't spam the API
            import time
            time.sleep(2)
            
        # Try a different model
        break  # For now, just test one endpoint

if __name__ == "__main__":
    test_gemini_search()

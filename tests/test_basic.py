import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.implementations import SimpleKeywordExtractor

def test_keyword_extraction():
    extractor = SimpleKeywordExtractor()
    question = "Find papers on osimertinib and glomerulonephritis"
    keywords = extractor.extract_keywords(question)

    assert "osimertinib" in keywords
    assert "glomerulonephritis" in keywords
    print("Keyword extraction test passed!")

if __name__ == "__main__":
    test_keyword_extraction()

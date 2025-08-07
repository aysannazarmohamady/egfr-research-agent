import gradio as gr
import os
from dotenv import load_dotenv
from core.interfaces import ResearchQuery

# Load environment variables
load_dotenv()
from core.implementations import SimpleContentAnalyzer, SimpleReportGenerator
from core.ai_implementations import GeminiKeywordExtractor, GeminiSourceRecommender
from core.pubmed_search import PubMedSearchEngine
from core.gemini_search import GeminiNativeSearchEngine

class ResearchAgentService:
    """Main research agent service with AI integration"""
    
    def __init__(self):
        # Initialize with AI-powered components
        try:
            self.keyword_extractor = GeminiKeywordExtractor()
            self.source_recommender = GeminiSourceRecommender()
            self.ai_enabled = True
        except ValueError as e:
            print(f"⚠️  AI components failed to initialize: {e}")
            print("📝 Falling back to simple implementations")
            # Fallback to simple implementations
            from core.implementations import SimpleKeywordExtractor, SimpleSourceRecommender
            self.keyword_extractor = SimpleKeywordExtractor()
            self.source_recommender = SimpleSourceRecommender()
            self.ai_enabled = False
        
        # Initialize search engines with Gemini native search
        try:
            self.search_engines = {
                "PubMed": PubMedSearchEngine(),
                "Google Scholar": GeminiNativeSearchEngine(),
                "Academic Search": GeminiNativeSearchEngine()
            }
        except Exception as e:
            print(f"⚠️ Gemini search initialization failed: {e}")
            self.search_engines = {
                "PubMed": PubMedSearchEngine()
            }
        self.content_analyzer = SimpleContentAnalyzer()
        self.report_generator = SimpleReportGenerator()
    
    def process_query(self, question: str) -> tuple:
        """Process research query and return results"""
        
        # Step 1: Extract keywords using AI
        keywords = self.keyword_extractor.extract_keywords(question)
        
        # Step 2: Recommend sources using AI
        sources = self.source_recommender.recommend_sources(keywords)
        
        return keywords, sources
    
    def execute_search(self, question: str, confirmed_keywords: str, confirmed_sources: str) -> str:
        """Execute the actual search and generate report"""
        
        # Parse confirmed inputs
        keywords = [k.strip() for k in confirmed_keywords.split(',')]
        sources = [s.strip() for s in confirmed_sources.split(',')]
        
        # Create query
        query = ResearchQuery(
            original_question=question,
            keywords=keywords,
            sources=sources
        )
        
        # Execute search
        all_results = []
        for source in sources:
            if source in self.search_engines:
                print(f"🔍 Searching {source}...")
                results = self.search_engines[source].search(keywords, source, limit=20)
                all_results.extend(results)
            else:
                print(f"⚠️ Search engine not available for: {source}")
        
        # Analyze results
        for result in all_results:
            result.relevance_score = self.content_analyzer.analyze_relevance(result, query)
            result.result_type = self.content_analyzer.classify_paper_type(result)
        
        # Generate report
        report = self.report_generator.generate_report(query, all_results)
        
        # Format output
        ai_status = "🤖 AI-Powered" if self.ai_enabled else "📝 Simple Mode"
        
        output = f"""
# Research Report ({ai_status})

## Query Summary
- **Original Question**: {report.query.original_question}
- **Keywords Used**: {', '.join(report.query.keywords)}
- **Sources Searched**: {', '.join(report.query.sources)}

## Results Overview
- **Total Papers Found**: {report.total_papers_found}
- **Relevant Papers**: {len(report.relevant_papers)}
- **Evidence Level**: {report.evidence_level}

## Summary
{report.summary}

## Key Findings
"""
        for i, finding in enumerate(report.key_findings, 1):
            output += f"{i}. {finding}\n"
        
        output += "\n## Recommendations\n"
        for i, rec in enumerate(report.recommendations, 1):
            output += f"{i}. {rec}\n"
        
        output += "\n## Relevant Papers\n"
        for paper in report.relevant_papers:
            output += f"- **{paper.title}** ({paper.journal}, {paper.publication_date})\n"
            output += f"  - Authors: {', '.join(paper.authors)}\n"
            output += f"  - Type: {paper.result_type.value}\n"
            output += f"  - Relevance Score: {paper.relevance_score:.2f}\n\n"
        
        return output

# Initialize service
agent = ResearchAgentService()

def step1_extract_keywords(question):
    """Step 1: Extract and show keywords using AI"""
    if not question.strip():
        return "", ""
    
    try:
        keywords, sources = agent.process_query(question)
        keywords_str = ', '.join(keywords)
        sources_str = ', '.join(sources)
        
        return keywords_str, sources_str
    except Exception as e:
        return f"Error: {str(e)}", ""

def step2_generate_report(question, keywords, sources):
    """Step 2: Generate final report"""
    if not all([question.strip(), keywords.strip(), sources.strip()]):
        return "Please fill in all fields from Step 1 first."
    
    try:
        report = agent.execute_search(question, keywords, sources)
        return report
    except Exception as e:
        return f"Error generating report: {str(e)}"

# Create Gradio interface
ai_status_text = "🤖 AI-Powered Mode" if agent.ai_enabled else "📝 Simple Mode (Set GEMINI_API_KEY to enable AI)"

with gr.Blocks(title="EGFR Research Agent") as demo:
    gr.Markdown("# 🔬 EGFR Research Agent")
    gr.Markdown("AI-powered research agent for EGFR inhibitor nephrotoxicity studies")
    gr.Markdown(f"**Status**: {ai_status_text}")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Step 1: Enter Your Research Question")
            question_input = gr.Textbox(
                label="Research Question",
                placeholder="e.g., Find papers on acute glomerulonephritis associated with EGFR inhibitors",
                lines=3
            )
            
            extract_btn = gr.Button("🔍 Extract Keywords & Sources", variant="primary")
            
            gr.Markdown("## Step 2: Review & Modify (Optional)")
            keywords_input = gr.Textbox(
                label="Keywords (comma-separated)",
                placeholder="AI-generated keywords will appear here...",
                lines=2
            )
            
            sources_input = gr.Textbox(
                label="Sources (comma-separated)", 
                placeholder="AI-recommended sources will appear here...",
                lines=2
            )
            
            search_btn = gr.Button("📊 Generate Research Report", variant="secondary")
        
        with gr.Column():
            gr.Markdown("## Research Report")
            output = gr.Markdown("Your AI-powered research report will appear here...")
    
    # Event handlers
    extract_btn.click(
        fn=step1_extract_keywords,
        inputs=[question_input],
        outputs=[keywords_input, sources_input]
    )
    
    search_btn.click(
        fn=step2_generate_report,
        inputs=[question_input, keywords_input, sources_input],
        outputs=[output]
    )

if __name__ == "__main__":
    # Environment variables are loaded automatically from .env file
    # No need to set API key manually - it's loaded from .env
    
    demo.launch(share=True)

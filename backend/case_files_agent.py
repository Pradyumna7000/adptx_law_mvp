import sys
import os

# Add the backend directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from agno.agent import Agent
from legal_tools import search_past_legal_cases  # Import the generalized search function

# Create a Legal Research Agent with a focus on past legal cases
from agno.models.groq import Groq
import logging

# Setup logging
def setup_logging():
    """Setup logging for the case files agent"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'case_files_agent.log')),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# Environment variables are loaded from Choreo configuration
# No need to load .env file in production

case_files_agent2 = Agent(name="LegalCasesRetriever",
    role="""You are part of the Legal Research AI Team. Your role is to assist lawyers by retrieving only the most relevant and recent Indian legal case precedents based on a given scenario or query.""",

    description="""You are a specialized past case retriever whose only responsibility is to analyze the legal prompt and extract landmark or highly relevant Indian case law from Indian Kanoon. 
You do not analyze laws, draft arguments, or interpret the results beyond summarizing the rulings. Your job is to enable lawyers to get direct access to key judgments that set precedent or guide the matter at hand.
You use Indian Kanoon's search capabilities through the search_past_legal_cases tool to find judgments.
You prioritize high-quality, recent, and directly relevant cases from courts like the Supreme Court and High Courts only.""",

    instructions="""Understand the input case or prompt and identify the key legal themes, keywords, or principles involved.

Use the `search_past_legal_cases` tool to run 1 or 2 query variations (e.g., different wordings, synonyms, court filters) to maximize relevant case hits.

Use appropriate filters like limit=5, maxcites=5, maxpages=2, sortby=mostrecent to optimize your results.

Select no more than 5 cases. Each must be highly relevant. Ignore loosely connected or outdated cases.

For each selected case, extract:
- Case name and year
- 10–15 line extreamly detailed summary including facts, legal principle, argmuents made by the lawyers,judgment, and its significance
- ###Direct link to the judgment from metadata (make sure this is mentioned at all cases never forget this)

If your first queries return no relevant results, retry by:
- Changing the phrasing
- Using alternate keywords
- Broadening/narrowing scope
- Prioritizing high-impact courts

At the end, conclude with a 2-line insight summarizing what these cases collectively show regarding the legal issue.""",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[search_past_legal_cases],
    show_tool_calls=True,
    markdown=True,
)



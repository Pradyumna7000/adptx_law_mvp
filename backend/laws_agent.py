"""
Laws Retrieval Agent

Retrieves relevant Indian laws, constitutional provisions, and statutory acts
for legal research and analysis.
"""

import sys
import os

# Add the backend directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from agno.agent import Agent
from agno.models.groq import Groq
from law_pdf_knowledge_base import pdf_knowledge_base
from kanoon_law_search import indian_kanoon_law_search
from dotenv import load_dotenv
import logging

# Try to import SqliteStorage, fallback to None if not available
try:
    from agno.storage.sqlite import SqliteStorage
    SQLITE_AVAILABLE = True
    print("SqliteStorage available in laws_agent")
except ImportError:
    SQLITE_AVAILABLE = False
    print("SqliteStorage not available in laws_agent (sqlalchemy missing)")

# Setup logging
def setup_logging():
    """Setup logging for the laws agent"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'laws_agent.log')),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize storage with proper path (optional)
storage = None
if SQLITE_AVAILABLE:
    try:
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        storage = SqliteStorage(table_name="law_session", db_file=os.path.join(data_dir, "law_data.db"))
        storage.create()
        print("Law agent storage initialized successfully")
    except Exception as e:
        print(f"Failed to initialize law agent storage: {e}")
        storage = None
else:
    print("Law agent running without persistent storage")

# Create laws retrieval agent
law_agent1 = Agent(
    name="LawsRetriever",
    role="Retrieve relevant Indian laws, constitutional provisions, and statutory acts",
    description="""Specialist in retrieving legal statutes and constitutional provisions.
    Extracts and lists relevant legal articles, sections, or acts that apply to the case.
    Provides exact law names, section numbers, verbatim text, and applicability explanations.
    Focuses on factual, law-based information without interpretation or speculation.""",
    instructions="""Analyze the case scenario and retrieve relevant laws:
    1. Search Indian Constitution and statutory documents in knowledge base
    2. Use Indian Kanoon tool for additional law retrieval if needed
    3. Ensure laws are up-to-date and in effect
    4. Include for each law:
       - Act/article name
       - Section/article number
       - Verbatim legal text
       - Relevance explanation
    5. Provide summary of how laws apply to the case
    
    Do NOT provide interpretations, summaries, or unrelated legal background.""",
    user_id="lawyer_user",
    model=Groq(id="llama-3.3-70b-versatile"),
    knowledge=pdf_knowledge_base,
    storage=storage,
    tools=[indian_kanoon_law_search],
    search_knowledge=True,
    markdown=True
)

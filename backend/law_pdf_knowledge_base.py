import os
import logging

# Try to import PDF knowledge base components
try:
    from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
    from agno.vectordb.lancedb import LanceDb
    from agno.embedder.ollama import OllamaEmbedder
    PDF_KNOWLEDGE_AVAILABLE = True
    print("✅ PDF knowledge base components available")
except ImportError as e:
    PDF_KNOWLEDGE_AVAILABLE = False
    print(f"⚠️ PDF knowledge base components not available: {e}")

# Setup logging
def setup_logging():
    """Setup logging for the law PDF knowledge base"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'law_pdf_knowledge.log')),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# Initialize PDF knowledge base (optional)
pdf_knowledge_base = None

if PDF_KNOWLEDGE_AVAILABLE:
    try:
        # Create data directories
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        # Define the vector database and embedder
        vector_db = LanceDb(
            table_name="legal_docs",
            uri=os.path.join(data_dir, "lancedb"),
            embedder=OllamaEmbedder(id="nomic-embed-text", dimensions=768),
        )

        # Setup the PDF knowledge base
        pdf_knowledge_base = PDFKnowledgeBase(
            path="legal-pdfs",
            vector_db=vector_db,
            reader=PDFReader(chunk=True)
        )

        # Load the knowledge base
        logger.info("Loading law PDF knowledge base...")
        pdf_knowledge_base.load(recreate=False)
        logger.info("Law PDF knowledge base loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize PDF knowledge base: {e}")
        pdf_knowledge_base = None
        print(f"⚠️ PDF knowledge base initialization failed: {e}")
else:
    logger.warning("⚠️ PDF knowledge base not available - running without PDF knowledge")
    print("⚠️ Running without PDF knowledge base")


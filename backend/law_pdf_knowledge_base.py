import os
import logging

# Try to import PDF knowledge base components
try:
    from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
    from agno.vectordb.lancedb import LanceDb
    from simple_embedder import SimpleEmbedder
    PDF_KNOWLEDGE_AVAILABLE = True
    print("PDF knowledge base components available")
except ImportError as e:
    PDF_KNOWLEDGE_AVAILABLE = False
    print(f"PDF knowledge base components not available: {e}")

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
        
        # Create legal-pdfs directory if it doesn't exist
        legal_pdfs_dir = "legal-pdfs"
        os.makedirs(legal_pdfs_dir, exist_ok=True)

        # Define the vector database and embedder
        vector_db = LanceDb(
            table_name="legal_docs",
            uri=os.path.join(data_dir, "lancedb"),
            embedder=SimpleEmbedder(dimensions=768),
        )

        # Setup the PDF knowledge base
        pdf_knowledge_base = PDFKnowledgeBase(
            path=legal_pdfs_dir,
            vector_db=vector_db,
            reader=PDFReader(chunk=True)
        )

        # Load the knowledge base (only if there are PDFs)
        logger.info("Loading law PDF knowledge base...")
        try:
            pdf_knowledge_base.load(recreate=False)
            logger.info("Law PDF knowledge base loaded successfully")
        except Exception as load_error:
            logger.warning(f"Could not load existing PDF knowledge base: {load_error}")
            logger.info("PDF knowledge base ready for new PDFs")
        
    except Exception as e:
        logger.error(f"Failed to initialize PDF knowledge base: {e}")
        pdf_knowledge_base = None
        print(f"PDF knowledge base initialization failed: {e}")
else:
    logger.warning("PDF knowledge base not available - running without PDF knowledge")
    print("Running without PDF knowledge base")

# Function to add PDF to knowledge base
def add_pdf_to_knowledge_base(pdf_path: str) -> bool:
    """Add a PDF to the knowledge base"""
    if pdf_knowledge_base is None:
        logger.error("PDF knowledge base not available")
        return False
    
    try:
        # Copy PDF to legal-pdfs directory
        import shutil
        filename = os.path.basename(pdf_path)
        dest_path = os.path.join("legal-pdfs", filename)
        shutil.copy2(pdf_path, dest_path)
        
        # Reload knowledge base
        pdf_knowledge_base.load(recreate=True)
        logger.info(f"Added PDF {filename} to knowledge base")
        return True
    except Exception as e:
        logger.error(f"Failed to add PDF to knowledge base: {e}")
        return False


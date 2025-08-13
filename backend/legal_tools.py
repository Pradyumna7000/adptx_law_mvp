"""
Legal Tools

Utility functions for legal research including case search and document retrieval.
"""

import sys
import os

# Add the backend directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import logging
import json
import codecs
from ikapi import IKApi, FileStorage, setup_logging

# Load .env file for local development (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file for local development")
except ImportError:
    print("python-dotenv not available, using environment variables directly")
except Exception as e:
    print(f"Could not load .env file: {e}")

# Environment variables are loaded from Choreo configuration in production

# Setup logging
def setup_legal_tools_logging():
    """Setup logging for legal tools"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'legal_tools.log')),
            logging.StreamHandler()
        ]
    )

setup_legal_tools_logging()
logger = logging.getLogger('legal_tools')

def search_past_legal_cases(query: str, limit: int = 10, maxpages: int = 2, maxcites: int = 5,
                            sortby: str = 'mostrecent', court: str = None) -> str:
    """Search for past legal cases on Indian Kanoon.
    
    Args:
        query: Search query (e.g., 'hindu divorce cases on domestic abuse')
        limit: Maximum number of cases to retrieve (default: 10)
        maxpages: Number of pages to retrieve (default: 2)
        maxcites: Maximum number of citations (default: 5)
        sortby: Sort order (default: 'mostrecent')
        court: Specific court to search (supreme, high, etc.)
    
    Returns:
        JSON string containing case metadata and fragments
    """
    # Setup logging
    setup_logging("info")
    logger = logging.getLogger('legal_case_search')

    data_dir = "kanoon_data"
    os.makedirs(data_dir, exist_ok=True)

    api_token = os.getenv("INDIAN_KANOON_API_KEY")
    if not api_token:
        logger.error("API token not found. Set INDIAN_KANOON_API_KEY in .env file (local) or Choreo environment configuration (production).")
        return json.dumps({"error": "API token not found."})

    class ApiArgs:
        def __init__(self):
            self.token = api_token
            self.maxpages = maxpages
            self.maxcites = maxcites
            self.maxcitedby = maxcites
            self.orig = False
            self.pathbysrc = False
            self.numworkers = 1
            self.addedtoday = False
            self.fromdate = None
            self.todate = None
            self.sortby = sortby

    api_args = ApiArgs()
    file_storage = FileStorage(data_dir)
    api_client = IKApi(api_args, file_storage)

    # If a specific court is provided, include it in the query
    if court:
        query += f" court:{court}"

    logger.info(f"Searching for: {query} with limit {limit}")

    def limited_search(query, limit):
        results = api_client.search(query, 0, maxpages)
        obj = json.loads(results)

        if 'errmsg' in obj:
            logger.warning(f"Error: {obj['errmsg']}")
            return json.dumps({"error": obj['errmsg']})

        docs = obj.get("docs", [])
        if not docs:
            logger.warning("No documents found")
            return json.dumps({"error": "No documents found"})

        docs = docs[:limit]
        limited_dir = os.path.join(data_dir, "limited_cases")
        os.makedirs(limited_dir, exist_ok=True)

        results_path = os.path.join(limited_dir, "legal_cases.json")
        with codecs.open(results_path, mode='w', encoding='utf-8') as f:
            json.dump({
                "query": query,
                "total_found": obj.get('found', 0),
                "limited_to": limit,
                "docs": docs
            }, f, indent=2)

        docids = []
        for i, doc in enumerate(docs, 1):
            docid = doc['tid']
            title = doc['title']
            publish_date = doc.get("publishdate", "Unknown Date")
            court = doc.get("docsource", "Unknown Court")
            doc_dir = os.path.join(limited_dir, f"case_{i}_id_{docid}")
            os.makedirs(doc_dir, exist_ok=True)

            metadata = {
                "id": docid,
                "title": title,
                "court": court,
                "date": publish_date,
                "position": i,
                "url": f"https://indiankanoon.org/doc/{docid}/"
            }

            meta_path = os.path.join(doc_dir, "metadata.json")
            with codecs.open(meta_path, mode='w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            # Extract document fragments and save them in a separate file
            fragments = doc.get("docfragments", [])
            if fragments:
                fragment_path = os.path.join(doc_dir, "doc_fragments.txt")
                with codecs.open(fragment_path, mode='w', encoding='utf-8') as f:
                    for idx, frag in enumerate(fragments, 1):
                        f.write(f"Fragment {idx}:\n{frag}\n\n{'-' * 60}\n\n")

            api_client.download_doc(docid, doc_dir)
            docids.append(docid)

        return json.dumps({
            "query": query,
            "total_found": obj.get('found', 0),
            "limited_to": limit,
            "docs": docs
        })

    return limited_search(query, limit)

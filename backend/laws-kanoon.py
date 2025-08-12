# kanoon_law_search.py

import os
import json
import codecs
import logging
from dotenv import load_dotenv
from ikapi import IKApi, FileStorage, setup_logging

load_dotenv()
logger = logging.getLogger("law_tool")
setup_logging("info")

def indian_kanoon_law_search(query: str, limit: int = 10) -> str:
    """
    Search for Indian laws (Bare Acts) using Indian Kanoon API.

    Args:
        query (str): Search query string (e.g., "section 377 IPC")
        limit (int): Max number of law documents to retrieve (default: 10)

    Returns:
        str: JSON string containing list of retrieved law documents.
    """

    api_token = os.getenv("INDIAN_KANOON_API_KEY")
    if not api_token:
        logger.error("API token not found. Set INDIAN_KANOON_API_KEY in .env file.")
        return json.dumps({"error": "API key missing"})

    data_dir = "law_data"
    os.makedirs(data_dir, exist_ok=True)
    file_storage = FileStorage(data_dir)

    class ApiArgs:
        def __init__(self):
            self.token = api_token
            self.maxpages = 2
            self.maxcites = 3
            self.maxcitedby = 3
            self.orig = False
            self.pathbysrc = False
            self.numworkers = 1
            self.addedtoday = False
            self.fromdate = None
            self.todate = None
            self.sortby = "relevance"

    api_args = ApiArgs()
    api_client = IKApi(api_args, file_storage)

    formatted_query = f"{query} site:indiankanoon.org/doc/ type:bareact"
    results = api_client.search(formatted_query, 0, api_args.maxpages)
    obj = json.loads(results)

    if "errmsg" in obj:
        logger.error(f"Error from API: {obj['errmsg']}")
        return json.dumps({"error": obj['errmsg']})

    docs = obj.get("docs", [])[:limit]
    laws_info = []

    for i, doc in enumerate(docs, 1):
        docid = doc["tid"]
        law_info = {
            "title": doc.get("title", "Untitled Law"),
            "date": doc.get("publishdate", "Unknown"),
            "url": f"https://indiankanoon.org/doc/{docid}/",
            "key_fragments": doc.get("docfragments", [])
        }
        laws_info.append(law_info)

    return json.dumps(laws_info, indent=2)

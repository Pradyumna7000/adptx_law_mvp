"""
Simple PDF RAG Agent for ADPTX
Integrates with orchestrator to provide PDF analysis and Q&A capabilities
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
import json
from datetime import datetime

# Try to import required components
try:
    from agno.models.groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class PDFRAGAgent:
    """
    Simple PDF RAG Agent that integrates with ADPTX orchestrator
    Provides document processing, chunking, and AI-powered analysis
    """
    
    def __init__(self):
        """Initialize PDF RAG Agent"""
        self.agent_name = "PDF RAG Agent"
        self.documents = {}  # Store processed documents
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
        # Initialize Groq LLM if available
        if GROQ_AVAILABLE:
            try:
                self.llm = Groq(id="qwen/qwen3-32b")
                logger.info("Groq LLM initialized for PDF RAG")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq LLM: {e}")
                self.llm = None
        else:
            self.llm = None
            logger.warning("Groq LLM not available - using fallback responses")
        
        logger.info(f"{self.agent_name} initialized")
    
    def run_with_monitoring(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Main entry point for orchestrator - follows ADPTX pattern"""
        try:
            start_time = datetime.now()
            
            # Parse the query to determine action
            if "upload" in query.lower() or "process" in query.lower():
                # Extract PDF path from query
                pdf_path = self._extract_pdf_path(query)
                if pdf_path and os.path.exists(pdf_path):
                    # Process the PDF first
                    process_result = self.process_pdf_document(pdf_path, session_id)
                    
                    if process_result["status"] == "success":
                        # Always try to answer the question if there's a question in the query
                        question_part = None
                        
                        # Extract the question part (everything before "Process PDF file")
                        if "Process PDF file" in query:
                            question_part = query.split("Process PDF file")[0].strip()
                        else:
                            question_part = query
                        
                        # Check if there's a meaningful question
                        if question_part and question_part != "explain." and len(question_part) > 5:
                            logger.info(f"Processing question: {question_part}")
                            # Use the most recent document for Q&A
                            latest_doc = max(self.documents.items(), key=lambda x: x[1]["created_at"])
                            doc_id = latest_doc[0]
                            result = self.answer_question(question_part, doc_id)
                            
                            # Merge the results
                            result["document_id"] = process_result.get("document_id")
                            result["chunks_count"] = process_result.get("chunks_count")
                            result["total_text_length"] = process_result.get("total_text_length")
                        elif question_part == "explain.":
                            # Default analysis for "explain."
                            logger.info("Processing default analysis for 'explain.'")
                            latest_doc = max(self.documents.items(), key=lambda x: x[1]["created_at"])
                            doc_id = latest_doc[0]
                            result = self.answer_question("Please analyze this PDF document and provide a comprehensive summary", doc_id)
                            
                            # Merge the results
                            result["document_id"] = process_result.get("document_id")
                            result["chunks_count"] = process_result.get("chunks_count")
                            result["total_text_length"] = process_result.get("total_text_length")
                        else:
                            logger.info("No meaningful question found, returning process result")
                            result = process_result
                    else:
                        result = process_result
                else:
                    result = {"status": "error", "error": "PDF file not found"}
            elif "summarize" in query.lower() or "summary" in query.lower():
                # Generate document summary
                doc_id = self._extract_document_id(query) or "latest"
                result = self.generate_document_summary(doc_id)
            else:
                # Question answering - try to find a document
                doc_id = self._extract_document_id(query)
                if not doc_id and self.documents:
                    # Use the most recent document if no specific ID provided
                    latest_doc = max(self.documents.items(), key=lambda x: x[1]["created_at"])
                    doc_id = latest_doc[0]
                    logger.info(f"Using latest document for Q&A: {doc_id}")
                
                if doc_id and doc_id in self.documents:
                    result = self.answer_question(query, doc_id)
                else:
                    result = {"status": "error", "error": "No document available for Q&A"}
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            result["agent"] = self.agent_name
            
            return result
            
        except Exception as e:
            logger.error(f"PDF RAG Agent error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.agent_name
            }
    
    def process_pdf_document(self, pdf_path: str, session_id: str = None) -> Dict[str, Any]:
        """Process a PDF document and create chunks"""
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Extract text from PDF
            text_content = self._extract_text_from_pdf(pdf_path)
            if not text_content:
                return {"status": "error", "error": "Failed to extract text from PDF"}
            
            # Create document ID
            doc_id = str(uuid.uuid4())
            
            # Create chunks
            chunks = self._create_chunks(text_content)
            
            # Store document and chunks
            self.documents[doc_id] = {
                "path": pdf_path,
                "text_content": text_content,
                "chunks": chunks,
                "total_chunks": len(chunks),
                "created_at": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            logger.info(f"PDF processed successfully: {len(chunks)} chunks created")
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_count": len(chunks),
                "total_text_length": len(text_content),
                "message": f"PDF processed into {len(chunks)} chunks"
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_document_summary(self, doc_id: str) -> Dict[str, Any]:
        """Generate a summary of the document"""
        try:
            if doc_id not in self.documents:
                return {"status": "error", "error": "Document not found"}
            
            doc = self.documents[doc_id]
            chunks = doc["chunks"]
            
            # Use first few chunks for summary
            summary_chunks = chunks[:5]
            summary_text = "\n\n".join(summary_chunks)
            
            if self.llm:
                # Generate AI summary
                prompt = f"""
                You are a legal expert. Please provide a comprehensive summary of this legal document using the following template structure:
                
                Document Content:
                {summary_text}
                
                **RESPONSE TEMPLATE - Follow this exact structure:**
                
                ### 🔍 **DETAILED ANALYSIS**
                
                **For CASE FILES:**
                - **Case Overview**: Parties, jurisdiction, key facts
                - **Legal Issues**: Main legal questions and disputes
                - **Applicable Laws**: Relevant statutes and precedents
                - **Arguments**: Key arguments from both sides
                - **Court Decision**: Judgment, reasoning, and legal principles
                - **Legal Impact**: Precedent value and implications
                
                **For CONTRACTS & AGREEMENTS:**
                - **Contract Overview**: Purpose, parties, scope
                - **Key Terms**: Essential clauses and conditions
                - **Legal Issues**: Potential problems and risks
                - **Compliance Check**: Regulatory requirements
                - **Recommendations**: Improvements and modifications
                - **Risk Assessment**: Enforceability and legal risks
                
                **For LEGAL DOCUMENTS (Acts/Regulations):**
                - **Document Overview**: Purpose, scope, applicability
                - **Key Provisions**: Important sections and clauses
                - **Legal Framework**: Context and related laws
                - **Compliance Requirements**: Obligations and procedures
                - **Practical Applications**: Real-world implementation
                - **Recent Updates**: Amendments or changes
                
                ### 💡 **KEY TAKEAWAYS**
                - 3-5 most important points
                - Critical legal considerations
                - Action items or next steps
                
                ### 📚 **REFERENCES & SOURCES**
                - Relevant legal citations
                - Case law references
                - Statutory provisions
                
                ### ⚠️ **IMPORTANT NOTES**
                - Legal disclaimers
                - Limitations of analysis
                - Recommendations for professional consultation
                """
                
                try:
                    from agno.models.base import Message
                    response = self.llm.invoke([Message(role="user", content=prompt)])
                    
                    if hasattr(response, 'content'):
                        summary = response.content.strip()
                    elif hasattr(response, 'choices') and response.choices:
                        summary = response.choices[0].message.content.strip()
                    elif hasattr(response, 'text'):
                        summary = response.text.strip()
                    else:
                        summary = "AI summary generation failed"
                        
                except Exception as e:
                    logger.warning(f"AI summary failed: {e}")
                    summary = self._generate_fallback_summary(summary_text)
            else:
                summary = self._generate_fallback_summary(summary_text)
            
            return {
                "status": "success",
                "summary": summary,
                "document_id": doc_id,
                "chunks_used": len(summary_chunks)
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def answer_question(self, question: str, doc_id: str) -> Dict[str, Any]:
        """Answer questions about the document using RAG"""
        try:
            if doc_id not in self.documents:
                return {"status": "error", "error": "Document not found"}
            
            doc = self.documents[doc_id]
            chunks = doc["chunks"]
            
            # Find relevant chunks (simple keyword matching for now)
            relevant_chunks = self._find_relevant_chunks(question, chunks)
            
            if not relevant_chunks:
                # If no relevant chunks found, return the first few chunks as context
                relevant_chunks = chunks[:3] if chunks else []
                if not relevant_chunks:
                    return {"status": "error", "error": "No document content available"}
            
            # Prepare context
            context = "\n\n".join(relevant_chunks)
            
            if self.llm:
                # Generate AI response
                prompt = f"""
                You are a legal expert. Answer this question based on the document content below using the following template structure:
                
                Document Context:
                {context}
                
                Question: {question}
                
                **RESPONSE TEMPLATE - Follow this exact structure:**
                
                ### 🔍 **DETAILED ANALYSIS**
                
                **For CASE FILES:** Focus on facts, legal issues, arguments, decisions, and implications
                **For CONTRACTS:** Focus on terms, risks, compliance, and recommendations
                **For LEGAL DOCUMENTS:** Focus on provisions, requirements, and practical applications
                
                Include relevant details, legal analysis, and practical implications from the document.
                
                ### 💡 **KEY TAKEAWAYS**
                - 3-5 most important points
                - Critical legal considerations
                - Action items or next steps
                
                ### 📚 **REFERENCES & SOURCES**
                - Relevant legal citations
                - Case law references
                - Statutory provisions
                
                ### ⚠️ **IMPORTANT NOTES**
                - Legal disclaimers
                - Limitations of analysis
                - Recommendations for professional consultation
                """
                
                try:
                    from agno.models.base import Message
                    response = self.llm.invoke([Message(role="user", content=prompt)])
                    
                    if hasattr(response, 'content'):
                        answer = response.content.strip()
                    elif hasattr(response, 'choices') and response.choices:
                        answer = response.choices[0].message.content.strip()
                    elif hasattr(response, 'text'):
                        answer = response.text.strip()
                    else:
                        answer = "AI response generation failed"
                        
                except Exception as e:
                    logger.warning(f"AI response failed: {e}")
                    answer = self._generate_fallback_answer(question, context)
            else:
                answer = self._generate_fallback_answer(question, context)
            
            return {
                "status": "success",
                "answer": answer,
                "question": question,
                "document_id": doc_id,
                "chunks_used": len(relevant_chunks),
                "sources": [{"chunk_index": i, "preview": chunk[:100] + "..."} for i, chunk in enumerate(relevant_chunks)]
            }
            
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF using available libraries"""
        try:
            if PYMUPDF_AVAILABLE:
                return self._extract_with_pymupdf(pdf_path)
            elif PYPDF_AVAILABLE:
                return self._extract_with_pypdf(pdf_path)
            else:
                return self._extract_with_fallback(pdf_path)
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return None
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF"""
        doc = fitz.open(pdf_path)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += f"\n--- Page {page_num + 1} ---\n"
            text_content += page.get_text()
            text_content += "\n"
        
        doc.close()
        return text_content
    
    def _extract_with_pypdf(self, pdf_path: str) -> str:
        """Extract text using PyPDF"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text_content = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += page.extract_text()
                text_content += "\n"
            
            return text_content
    
    def _extract_with_fallback(self, pdf_path: str) -> str:
        """Fallback text extraction"""
        try:
            # Try to read as text first
            with open(pdf_path, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            try:
                # Try to read as binary and decode
                with open(pdf_path, 'rb') as file:
                    content = file.read()
                    return content.decode('utf-8', errors='ignore')
            except:
                # If all else fails, return a placeholder with file info
                try:
                    file_size = os.path.getsize(pdf_path)
                    return f"PDF Document Content\nFile: {os.path.basename(pdf_path)}\nSize: {file_size} bytes\n\nThis is a PDF document that has been uploaded for analysis. The content extraction is limited due to missing PDF processing libraries.\n\nFor full PDF analysis, please install: pip install pypdf pymupdf"
                except:
                    return "PDF content (text extraction not available)"
    
    def _create_chunks(self, text: str) -> List[str]:
        """Create text chunks for RAG"""
        chunks = []
        
        # Simple chunking by paragraphs
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if len(para) < 50:  # Skip very short paragraphs
                continue
            
            # Split long paragraphs
            if len(para) > self.chunk_size:
                words = para.split()
                current_chunk = ""
                
                for word in words:
                    if len(current_chunk + " " + word) <= self.chunk_size:
                        current_chunk += (" " + word) if current_chunk else word
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = word
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks.append(para)
        
        return chunks
    
    def _find_relevant_chunks(self, question: str, chunks: List[str]) -> List[str]:
        """Find relevant chunks using simple keyword matching"""
        question_lower = question.lower()
        question_words = set(question_lower.split())
        
        relevant_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            relevance_score = 0
            
            # Score based on word overlap
            for word in question_words:
                if len(word) > 3 and word in chunk_lower:
                    relevance_score += 1
            
            # Boost for exact phrase matches
            if question_lower in chunk_lower:
                relevance_score += 5
            
            if relevance_score > 0:
                relevant_chunks.append(chunk)
        
        # Return top 3 most relevant chunks
        return relevant_chunks[:3]
    
    def _generate_fallback_summary(self, text: str) -> str:
        """Generate fallback summary without AI"""
        lines = text.split('\n')
        summary_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['section', 'article', 'clause', 'act', 'law']):
                summary_lines.append(line.strip())
        
        if summary_lines:
            return "Document Summary:\n" + "\n".join(summary_lines[:10])
        else:
            return f"Document Summary:\nTotal content length: {len(text)} characters\nContent preview: {text[:500]}..."
    
    def _generate_fallback_answer(self, question: str, context: str) -> str:
        """Generate fallback answer without AI"""
        if "analyze" in question.lower() or "summary" in question.lower():
            return f"Document Analysis Summary:\n\nBased on the document content ({len(context)} characters):\n\n{context[:1000]}...\n\nThis document has been processed and is ready for detailed analysis. The content includes various sections that can be explored further."
        elif "what" in question.lower() or "explain" in question.lower():
            return f"Document Content Explanation:\n\n{context[:800]}...\n\nThis document contains relevant information that addresses your question. For more detailed analysis, please ask specific questions about particular sections."
        else:
            return f"Document Response:\n\n{context[:600]}...\n\nQuestion: {question}\n\nThis response is based on the document content. For more detailed analysis, please ask specific questions."
    
    def _extract_pdf_path(self, query: str) -> Optional[str]:
        """Extract PDF file path from query"""
        # Simple extraction - look for common patterns
        words = query.split()
        
        # First, look for exact PDF files
        for word in words:
            if word.lower().endswith('.pdf'):
                # Check if it's a relative path
                if os.path.exists(word):
                    return word
                # Check if it's in ai_systems directory
                ai_systems_path = f"ai_systems/{word}"
                if os.path.exists(ai_systems_path):
                    return ai_systems_path
                # Check if it's in uploads directory
                uploads_path = f"uploads/{word}"
                if os.path.exists(uploads_path):
                    return uploads_path
        
        # Look for patterns like "file path" or "PDF path"
        for i, word in enumerate(words):
            if i > 0 and words[i-1].lower() in ['file', 'pdf', 'document']:
                if os.path.exists(word):
                    return word
                # Check if it's in ai_systems directory
                ai_systems_path = f"ai_systems/{word}"
                if os.path.exists(ai_systems_path):
                    return ai_systems_path
                # Check if it's in uploads directory
                uploads_path = f"uploads/{word}"
                if os.path.exists(uploads_path):
                    return uploads_path
        
        # Look for uploads pattern
        if "uploads" in query:
            # Extract the filename after uploads
            import re
            uploads_pattern = r'uploads[\\\/]([^\\\/\s]+\.pdf)'
            match = re.search(uploads_pattern, query)
            if match:
                filename = match.group(1)
                uploads_path = f"uploads/{filename}"
                if os.path.exists(uploads_path):
                    return uploads_path
                
                # If exact match not found, look for files with similar names
                uploads_dir = "uploads"
                if os.path.exists(uploads_dir):
                    for file in os.listdir(uploads_dir):
                        if file.endswith('.pdf'):
                            # Check if the filename contains the requested name
                            if filename.lower() in file.lower() or file.lower().endswith(filename.lower()):
                                return os.path.join(uploads_dir, file)
            
            # If no specific filename found, try to find any PDF in uploads
            uploads_dir = "uploads"
            if os.path.exists(uploads_dir):
                pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
                if pdf_files:
                    # Return the most recent PDF file
                    pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)
                    return os.path.join(uploads_dir, pdf_files[0])
        
        # Special case for test queries
        if "sample.pdf" in query:
            sample_path = "ai_systems/sample.pdf"
            if os.path.exists(sample_path):
                return sample_path
        
        return None
    
    def _extract_document_id(self, query: str) -> Optional[str]:
        """Extract document ID from query"""
        # Look for UUID-like patterns
        import re
        uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        match = re.search(uuid_pattern, query)
        return match.group(0) if match else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics for orchestrator"""
        return {
            "agent_name": self.agent_name,
            "documents_processed": len(self.documents),
            "total_chunks": sum(doc["total_chunks"] for doc in self.documents.values()),
            "groq_available": GROQ_AVAILABLE,
            "pypdf_available": PYPDF_AVAILABLE,
            "pymupdf_available": PYMUPDF_AVAILABLE
        }

# Global instance for orchestrator
pdf_rag_agent = PDFRAGAgent()

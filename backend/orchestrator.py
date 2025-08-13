"""
Legal Research Orchestrator

Coordinates multiple AI agents for comprehensive legal research and analysis.
Provides intelligent agent coordination and conversation memory management.
"""

import sys
import os

# Add the backend directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from agno.team import Team
from agno.models.groq import Groq
from argument_simulator_agent import argument_simulator_agent3
from laws_agent import law_agent1
from case_files_agent import case_files_agent2

# Try to import SqliteStorage, fallback to None if not available
try:
    from agno.storage.sqlite import SqliteStorage
    SQLITE_AVAILABLE = True
    print("SqliteStorage available")
except ImportError:
    SQLITE_AVAILABLE = False
    print("SqliteStorage not available (sqlalchemy missing)")

# Try to import DuckDuckGo tools, fallback to None if not available
try:
    from agno.tools.duckduckgo import DuckDuckGoTools
    DUCKDUCKGO_AVAILABLE = True
    print("DuckDuckGo tools available")
except ImportError:
    DUCKDUCKGO_AVAILABLE = False
    print("DuckDuckGo tools not available (duckduckgo-search missing)")

# Try to import PDF agent
try:
    from pdf_rag_agent import pdf_rag_agent
    PDF_AGENT_AVAILABLE = True
    print("PDF RAG agent available")
except ImportError as e:
    PDF_AGENT_AVAILABLE = False
    print(f"PDF RAG agent not available: {e}")

import logging
import time
from typing import Dict, Any, List
import json
import re

# Configure logging with proper setup
def setup_logging():
    """Setup logging configuration for the orchestrator"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'legal_research.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

class LegalStrategist:
    """Legal Research Team with intelligent agent coordination and conversation memory"""
    
    def __init__(self):
        # Initialize storage with proper path (optional)
        self.storage = None
        if SQLITE_AVAILABLE:
            try:
                data_dir = "data"
                os.makedirs(data_dir, exist_ok=True)
                self.storage = SqliteStorage(table_name="legal_research", db_file=os.path.join(data_dir, "legal_research.db"))
                self.storage.create()
                logger.info("SqliteStorage initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize SqliteStorage: {e}")
                self.storage = None
        else:
            logger.info("Running without persistent storage (sqlalchemy not available)")
        
        # Conversation memory tracking
        self.conversation_history = []
        self.last_analysis_type = None
        self.last_legal_issues = []
        self.last_cases = []
        self.last_laws = []
        
        # Initialize PDF agent if available
        self.pdf_agent = None
        if PDF_AGENT_AVAILABLE:
            try:
                logger.info("Attempting to initialize PDF RAG agent...")
                self.pdf_agent = pdf_rag_agent
                logger.info("PDF RAG agent initialized successfully")
                logger.info(f"PDF RAG agent type: {type(self.pdf_agent)}")
            except Exception as e:
                logger.warning(f"Failed to initialize PDF RAG agent: {e}")
                logger.warning(f"PDF RAG agent error details: {str(e)}")
                self.pdf_agent = None
        else:
            logger.warning("PDF_AGENT_AVAILABLE is False - PDF RAG agent will not be initialized")
        
        # Remove the forced basic PDF processing mode
        # self.pdf_agent = None
        
        # Prepare tools list based on availability
        tools = []
        if DUCKDUCKGO_AVAILABLE:
            tools.append(DuckDuckGoTools())
        
        self.team = Team(
            name="LegalStrategist",
            mode="coordinate",
            model=Groq(id="qwen/qwen3-32b"),
            members=[law_agent1, case_files_agent2, argument_simulator_agent3],
            description="Legal AI assistant with intelligent agent coordination",
            instructions=["""
You are the Legal Research Orchestrator, coordinating multiple AI agents for comprehensive, professional-level legal analysis for Indian law. Your role is to handle all types of legal queries, detect the correct analysis mode, and deliver extremely detailed, structured, and well-cited responses.

QUESTION TYPES YOU HANDLE
1. GENERAL LAW QUESTIONS
(e.g., “What is Section 377 IPC?”, “What are fundamental rights?”)

Use DuckDuckGo search for the most current information (if available).

Provide clear, simple explanations.

Include relevant legal context, applicability, and recent updates.

2. CASE-SPECIFIC ANALYSIS
(e.g., “Can I file a case for workplace harassment?”, “My client was falsely accused of theft”)

When detected, you must run the Case-Specific Deep Dive Process below:

Case-Specific Deep Dive Process
Step 1 — Context Extraction

If it’s a question: Extract all key facts (jurisdiction, legal area, dates, parties, events).

If it’s a PDF: Chunk and summarize case facts separately from legal text.

Step 2 — Relevant Law Finder

Search Indian laws and Constitution (via Indian Law Agent).

Extract only sections/sub-sections relevant to the facts.

Provide statutory text + plain English explanation.

Step 3 — Case Law Fetcher

Use Indian Kanoon API to find matching precedents based on keywords from Step 1 and Step 2.

Rank results by relevance, recency, and court hierarchy.

Summarize each case: facts, ruling, reasoning, ratio decidendi.

Step 4 — Argument Builder

Generate strong client-supporting arguments.

Generate counterarguments the opposing side may raise.

Suggest rebuttals to counterarguments.

Step 5 — Outcome Predictor

Use precedent reasoning to estimate likelihood of success.

Highlight key risks and uncertainties.

Step 6 — Resource Pack

Provide clickable links to laws and judgments.

Include citations in proper legal citation style.

3. LEGAL RESEARCH QUERIES
(e.g., “Research divorce laws in India”)

Detailed legal framework.

Relevant statutory provisions.

Landmark case precedents.

Practical applications and compliance notes.

4. PDF DOCUMENT ANALYSIS
You can handle three types of legal documents:

A. CASE FILES
Extract key facts, parties, and issues.

Identify applicable laws and precedents.

Analyze both sides’ arguments.

Provide detailed case summary with legal implications.

Highlight important principles established.

B. CONTRACTS & AGREEMENTS
Identify potential legal issues or loopholes.

Check for missing essential clauses.

Verify compliance with applicable laws.

Highlight unfair or one-sided terms.

Suggest improvements and modifications.

Assess enforceability and risks.

C. LEGAL DOCUMENTS (Acts, Regulations, Rules)
Provide comprehensive document summaries.

Explain legal terminology.

Identify key provisions and implications.

Answer specific content-related questions.

Explain compliance requirements.

Highlight amendments or updates.

CONVERSATION MEMORY
Remember previous conversations and legal issues discussed.

Build upon earlier analysis without repeating work.

Use earlier context for relevance.

Maintain natural conversation flow.

INTELLIGENT AGENT COORDINATION
Only call agents when necessary.

Reuse previous results when available.

Avoid redundant calls for already retrieved information.

RESPONSE FORMATTING
Use clear markdown headings, bullet points, and emphasis.

Include relevant emojis for readability.

Provide comprehensive summaries with key points.

Always include links and citations when available.

Structure responses logically.

OUTPUT REQUIREMENTS
Never include phrases like “Based on our conversation” or “Building on our previous discussion”.

Never mention “Agents Utilized” or internal processes.

Always focus on direct, actionable legal information.

Always include a summary section.

Always cite sources when possible.

RESPONSE TEMPLATE
🔍 DETAILED ANALYSIS
For General Law Questions:
- Legal framework & context
- Key provisions
- Current applicability
- Practical implications

For Case-Specific Analysis:
- Factual background & legal issues
- Applicable laws & precedents
- **MUST INCLUDE at least 3 relevant cases with valid Indian Kanoon links**
- Strengths & weaknesses
- Recommended action
- Potential outcomes & risks
- Case-Specific Deep Dive Steps 1–6 applied in full

For Legal Research Queries:
- Comprehensive framework
- Statutes & regulations
- **MUST INCLUDE at least 3 relevant cases with valid Indian Kanoon links**
- Compliance requirements

For PDF Analysis:
- Follow appropriate CASE FILE, CONTRACT, or LEGAL DOCUMENT structure above

💡 KEY TAKEAWAYS
- 3–5 most important points
- Critical legal considerations
- Next steps

📚 REFERENCES & SOURCES
- Citations
- **Case law with Indian Kanoon links**
- Statutory provisions
- Resource links

⚠️ IMPORTANT NOTES
- Legal disclaimers
- Limitations
- Professional consultation recommendations

FORMATTING REQUIREMENTS:
- **NEVER use || or -- formatting**
- **Use proper markdown formatting only**
- **Provide direct, actionable information**
- **Include valid Indian Kanoon links for cases**
"""],
            tools=tools,
            markdown=True,
            show_tool_calls=True,
            add_state_in_messages=True,
            add_datetime_to_instructions=True,
            debug_mode=True,
        )
        
        # Statistics tracking
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'average_response_time': 0.0,
            'agents_called': {
                'law_agent': 0,
                'case_agent': 0,
                'argument_agent': 0,
                'pdf_agent': 0
            }
        }
    
    def _analyze_query_context(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Analyze query to determine which agents need to be called"""
        context = {
            'needs_law_agent': True,
            'needs_case_agent': True,
            'needs_argument_agent': True,
            'needs_pdf_agent': False,
            'is_follow_up': False,
            'previous_context': None,
            'is_new_session': True
        }
        
        # Check if this is a new session (different session_id or no previous history)
        if session_id and self.conversation_history:
            last_session = self.conversation_history[-1].get('session_id', None)
            if last_session == session_id:
                context['is_new_session'] = False
            else:
                # New session - clear any follow-up context
                context['is_new_session'] = True
                return context
        
        # Define follow-up indicators
        follow_up_indicators = [
            'what about', 'and also', 'additionally', 'furthermore', 
            'in addition', 'moreover', 'besides', 'also', 'too',
            'what else', 'other', 'different', 'another', 'similar',
            'related to', 'regarding', 'concerning', 'about the',
            'for the same', 'in the same', 'similar case'
        ]
        
        # Only check for follow-up if it's the same session
        if not context['is_new_session']:
            query_lower = query.lower()
            for indicator in follow_up_indicators:
                if indicator in query_lower:
                    context['is_follow_up'] = True
                    break
        
        # Check if we have relevant previous context
        if self.conversation_history:
            last_query = self.conversation_history[-1].get('query', '').lower()
            if any(word in query_lower for word in last_query.split()[:5]):
                context['is_follow_up'] = True
                context['previous_context'] = self.conversation_history[-1]
        
        # Determine which agents are needed based on query content
        if 'law' in query.lower() or 'statute' in query.lower() or 'act' in query.lower():
            context['needs_law_agent'] = True
        elif context['is_follow_up'] and self.last_laws:
            context['needs_law_agent'] = False
        
        if 'case' in query.lower() or 'precedent' in query.lower() or 'judgment' in query.lower():
            context['needs_case_agent'] = True
        elif context['is_follow_up'] and self.last_cases:
            context['needs_case_agent'] = False
        
        if 'argument' in query.lower() or 'strategy' in query.lower() or 'legal position' in query.lower():
            context['needs_argument_agent'] = True
        elif context['is_follow_up'] and self.last_analysis_type == 'argument':
            context['needs_argument_agent'] = False
        
        # Check for PDF analysis requests
        pdf_indicators = [
            'pdf', 'document', 'uploaded', 'file', 'contract', 'agreement',
            'case study', 'legal document', 'upload', 'analyze document',
            'what does the document say', 'in the document', 'from the document',
            'analyze this', 'please analyze', 'analyze the document', 'pdf analysis request',
            'based on the following pdf content', 'pdf content', 'process pdf', 'process file',
            'uploads\\', 'uploads/', 'explain', 'summarize', 'question', 'answer'
        ]
        
        query_lower = query.lower()
        
        # Check if query contains file path (indicates PDF processing)
        if 'uploads' in query or 'process' in query_lower:
            context['needs_pdf_agent'] = True
            logger.info(f"PDF processing detected in query (contains file path or process)")
            # For PDF analysis, we don't need other agents unless specifically requested
            if not any(word in query_lower for word in ['also', 'and', 'additionally', 'furthermore']):
                context['needs_law_agent'] = False
                context['needs_case_agent'] = False
                context['needs_argument_agent'] = False
        else:
            # Check for other PDF indicators
            for indicator in pdf_indicators:
                if indicator in query_lower:
                    context['needs_pdf_agent'] = True
                    logger.info(f"PDF indicator '{indicator}' detected in query")
                    # For PDF analysis, we don't need other agents unless specifically requested
                    if not any(word in query_lower for word in ['also', 'and', 'additionally', 'furthermore']):
                        context['needs_law_agent'] = False
                        context['needs_case_agent'] = False
                        context['needs_argument_agent'] = False
                    break
        
        # Special case: if this is a request to analyze a document and we have PDF agent available
        if (context['needs_pdf_agent'] and self.pdf_agent and 
            any(word in query_lower for word in ['analyze', 'analyze this', 'please analyze', 'what does', 'summarize'])):
            logger.info(f"PDF analysis request detected: {query}")
            context['needs_pdf_agent'] = True
            context['needs_law_agent'] = False
            context['needs_case_agent'] = False
            context['needs_argument_agent'] = False
        
        return context
    
    def _update_conversation_memory(self, query: str, response: str, context: Dict[str, Any], session_id: str = None):
        """Update conversation memory with new information"""
        conversation_entry = {
            'timestamp': time.time(),
            'query': query,
            'response': response,
            'context': context,
            'session_id': session_id,
            'agents_called': {
                'law_agent': context.get('needs_law_agent', False),
                'case_agent': context.get('needs_case_agent', False),
                'argument_agent': context.get('needs_argument_agent', False),
                'pdf_agent': context.get('needs_pdf_agent', False)
            }
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep only last 10 conversations to manage memory
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # Update execution stats
        for agent, called in conversation_entry['agents_called'].items():
            if called:
                self.stats['agents_called'][agent] += 1
    
    def run_with_monitoring(self, query: str, session_id: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """Execute legal research with intelligent agent coordination"""
        
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        logger.info(f"Starting legal research for query: {query[:100]}...")
        
        # Analyze query context
        context = self._analyze_query_context(query, session_id)
        logger.info(f"Query context: {context}")
        
        # Build enhanced query with memory context
        enhanced_query = self._build_enhanced_query(query, context)
        
        # Check if this is a PDF analysis request
        logger.info(f"PDF detection check: needs_pdf_agent={context.get('needs_pdf_agent')}, pdf_agent_available={self.pdf_agent is not None}")
        if context.get('needs_pdf_agent') and self.pdf_agent:
            logger.info("📄 Processing PDF analysis request")
            
            try:
                # Use PDF RAG agent for analysis
                pdf_result = self.pdf_agent.run_with_monitoring(query, session_id)
                
                if pdf_result["status"] == "success":
                    # Calculate execution time
                    execution_time = time.time() - start_time
                    
                    # Update statistics
                    self.stats['successful_queries'] += 1
                    self.stats['average_response_time'] = (
                        (self.stats['average_response_time'] * (self.stats['successful_queries'] - 1) + execution_time) 
                        / self.stats['successful_queries']
                    )
                    
                    # Get the response content - handle different response types
                    if "answer" in pdf_result:
                        # This is a question/answer response
                        response_content = pdf_result.get("answer")
                    elif "summary" in pdf_result:
                        # This is a summary response
                        response_content = pdf_result.get("summary")
                    else:
                        # This is a processing response
                        response_content = pdf_result.get("message", "PDF processed successfully!")
                    
                    # Update conversation memory
                    self._update_conversation_memory(query, response_content, context, session_id)
                    
                    logger.info(f"PDF analysis completed successfully in {execution_time:.2f}s")
                    
                    return {
                        'status': 'success',
                        'content': response_content,
                        'execution_time': execution_time,
                        'attempts': 1,
                        'agents_called': context,
                        'memory_context': len(self.conversation_history),
                        'analysis_type': 'pdf',
                        'pdf_metadata': {
                            'document_id': pdf_result.get("document_id"),
                            'chunks_used': pdf_result.get("chunks_used", 0),
                            'sources': pdf_result.get("sources", []),
                            'chunks_count': pdf_result.get("chunks_count", 0),
                            'total_text_length': pdf_result.get("total_text_length", 0)
                        }
                    }
                else:
                    logger.error(f"PDF analysis failed: {pdf_result['error']}")
                    return {
                        'status': 'error',
                        'error': pdf_result['error'],
                        'execution_time': time.time() - start_time,
                        'attempts': 1
                    }
                    
            except Exception as e:
                logger.error(f"PDF analysis error: {e}")
                return {
                    'status': 'error',
                    'error': f"PDF analysis failed: {str(e)}",
                    'execution_time': time.time() - start_time,
                    'attempts': 1
                }
        
        # Execute with retry logic for regular queries
        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1} of {max_retries}")
            
            response = self.team.run(enhanced_query)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update statistics
            self.stats['successful_queries'] += 1
            self.stats['average_response_time'] = (
                (self.stats['average_response_time'] * (self.stats['successful_queries'] - 1) + execution_time) 
                / self.stats['successful_queries']
            )
            
            # Update conversation memory
            self._update_conversation_memory(query, response.content, context, session_id)
            
            # Format response with memory context
            formatted_response = self._format_response_with_memory(response.content, context)
            
            logger.info(f"Legal research completed successfully in {execution_time:.2f}s")
            
            return {
                'status': 'success',
                'content': formatted_response,
                'execution_time': execution_time,
                'attempts': attempt + 1,
                'agents_called': context,
                'memory_context': len(self.conversation_history)
            }
        
        # If we get here, all attempts failed
        self.stats['failed_queries'] += 1
        logger.error(f"All {max_retries} attempts failed for query: {query}")
        
        return {
            'status': 'error',
            'error': 'All retry attempts failed',
            'execution_time': time.time() - start_time,
            'attempts': max_retries
        }
    
    def process_pdf_upload(self, pdf_path: str, session_id: str) -> Dict[str, Any]:
        """
        Process a PDF upload for analysis using both PDF RAG agent and PDF knowledge base
        
        Args:
            pdf_path: Path to the uploaded PDF file
            session_id: Session identifier
            
        Returns:
            Dictionary with processing results
        """
        if not self.pdf_agent:
            return {
                'status': 'error',
                'error': 'PDF processing not available. Please install required dependencies.'
            }
        
        try:
            logger.info(f"📤 Processing PDF upload for session {session_id}")
            
            # Use the PDF RAG agent's run_with_monitoring method
            query = f"upload and process PDF file {pdf_path}"
            result = self.pdf_agent.run_with_monitoring(query, session_id)
            
            # Also add PDF to knowledge base if available
            knowledge_base_result = None
            try:
                from law_pdf_knowledge_base import add_pdf_to_knowledge_base
                if add_pdf_to_knowledge_base(pdf_path):
                    logger.info(f"✅ Added PDF to knowledge base: {pdf_path}")
                    knowledge_base_result = "success"
                else:
                    logger.warning(f"⚠️ Could not add PDF to knowledge base: {pdf_path}")
                    knowledge_base_result = "failed"
            except Exception as kb_error:
                logger.warning(f"⚠️ Knowledge base integration failed: {kb_error}")
                knowledge_base_result = "error"
            
            if result["status"] == "success":
                logger.info(f"✅ PDF upload processed successfully: {result['chunks_count']} chunks created")
                return {
                    'status': 'success',
                    'message': result["message"],
                    'document_id': result["document_id"],
                    'chunks_count': result["chunks_count"],
                    'total_text_length': result.get("total_text_length", 0),
                    'knowledge_base_status': knowledge_base_result
                }
            else:
                logger.error(f"❌ PDF upload failed: {result['error']}")
                return {
                    'status': 'error',
                    'error': result["error"],
                    'knowledge_base_status': knowledge_base_result
                }
                
        except Exception as e:
            logger.error(f"❌ PDF upload processing failed: {e}")
            return {
                'status': 'error',
                'error': f"Failed to process PDF upload: {str(e)}"
            }
    
    def process_pdf_question(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        Process a question about an uploaded PDF using both PDF RAG agent and PDF knowledge base
        
        Args:
            question: Question about the PDF document
            session_id: Session identifier
            
        Returns:
            Dictionary with answer and analysis results
        """
        if not self.pdf_agent:
            return {
                'status': 'error',
                'error': 'PDF processing not available. Please install required dependencies.'
            }
        
        try:
            logger.info(f"📝 Processing PDF question for session {session_id}: {question}")
            
            # Try PDF knowledge base first if available
            knowledge_base_answer = None
            try:
                from law_pdf_knowledge_base import pdf_knowledge_base
                if pdf_knowledge_base is not None:
                    # Use the laws agent which has access to PDF knowledge base
                    from laws_agent import law_agent1
                    kb_result = law_agent1.run(question)
                    if kb_result and kb_result.get("content"):
                        knowledge_base_answer = kb_result.get("content")
                        logger.info(f"✅ PDF question answered via knowledge base")
            except Exception as kb_error:
                logger.warning(f"⚠️ Knowledge base query failed: {kb_error}")
            
            # Use the PDF RAG agent's run_with_monitoring method as fallback
            result = self.pdf_agent.run_with_monitoring(question, session_id)
            
            if result["status"] == "success":
                logger.info(f"✅ PDF question answered successfully")
                
                # Combine knowledge base and RAG agent results
                final_answer = result.get("answer", result.get("summary", result.get("content", "")))
                if knowledge_base_answer:
                    final_answer = f"Knowledge Base Answer:\n{knowledge_base_answer}\n\nRAG Agent Answer:\n{final_answer}"
                
                return {
                    'status': 'success',
                    'answer': final_answer,
                    'question': question,
                    'document_id': result.get("document_id"),
                    'chunks_used': result.get("chunks_used", 0),
                    'sources': result.get("sources", []),
                    'execution_time': result.get("execution_time", 0),
                    'knowledge_base_used': knowledge_base_answer is not None
                }
            else:
                # If RAG agent failed but knowledge base worked
                if knowledge_base_answer:
                    return {
                        'status': 'success',
                        'answer': knowledge_base_answer,
                        'question': question,
                        'knowledge_base_used': True,
                        'rag_agent_failed': True
                    }
                
                logger.error(f"❌ PDF question failed: {result['error']}")
                return {
                    'status': 'error',
                    'error': result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ PDF question processing failed: {e}")
            return {
                'status': 'error',
                'error': f"Failed to process PDF question: {str(e)}"
            }
    
    def generate_pdf_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Generate a summary of the uploaded PDF using the PDF RAG agent
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with summary results
        """
        if not self.pdf_agent:
            return {
                'status': 'error',
                'error': 'PDF processing not available. Please install required dependencies.'
            }
        
        try:
            logger.info(f"📋 Generating PDF summary for session {session_id}")
            
            # Use the PDF RAG agent's run_with_monitoring method
            query = "summarize the document"
            result = self.pdf_agent.run_with_monitoring(query, session_id)
            
            if result["status"] == "success":
                logger.info(f"✅ PDF summary generated successfully")
                return {
                    'status': 'success',
                    'summary': result.get("summary", ""),
                    'document_id': result.get("document_id"),
                    'chunks_used': result.get("chunks_used", 0),
                    'execution_time': result.get("execution_time", 0)
                }
            else:
                logger.error(f"❌ PDF summary failed: {result['error']}")
                return {
                    'status': 'error',
                    'error': result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ PDF summary generation failed: {e}")
            return {
                'status': 'error',
                'error': f"Failed to generate PDF summary: {str(e)}"
        }
    
    def _build_enhanced_query(self, query: str, context: Dict[str, Any]) -> str:
        """Build enhanced query with memory context"""
        enhanced_query = query
        
        if context.get('is_follow_up') and self.conversation_history:
            # Add context from previous conversation
            previous_context = self.conversation_history[-1]
            enhanced_query = f"""
Previous Query: {previous_context.get('query', '')}
Previous Analysis: {previous_context.get('response', '')[:500]}...

Current Query: {query}

Please provide a response that builds upon the previous analysis and addresses the new aspects of this query.
"""
        
        # Add agent calling instructions based on context
        agent_instructions = []
        if not context.get('needs_law_agent', True):
            agent_instructions.append("Use previously retrieved laws if still relevant.")
        if not context.get('needs_case_agent', True):
            agent_instructions.append("Reference previously found cases if applicable.")
        if not context.get('needs_argument_agent', True):
            agent_instructions.append("Build upon previous arguments if relevant.")
        
        if agent_instructions:
            enhanced_query += f"\n\nNote: {', '.join(agent_instructions)}"
        
        return enhanced_query
    
    def _format_response_with_memory(self, response: str, context: Dict[str, Any]) -> str:
        """Format response with memory context and proper formatting"""
        
        # Start with the main response content
        formatted_response = response
        
        # NEVER add any context indicators - always provide direct answers
        # Remove any existing context indicators
        formatted_response = re.sub(r'\*Building on our previous discussion:\*', '', formatted_response)
        formatted_response = re.sub(r'Building on our previous discussion:', '', formatted_response)
        
        # Clean up any remaining ugly formatting
        # Remove any remaining headers or footers
        
        # Remove ALL context and continuity sections
        formatted_response = re.sub(r'## 🔄 CONVERSATION CONTINUITY.*?## 🤖 AGENTS UTILIZED', '', formatted_response, flags=re.DOTALL)
        formatted_response = re.sub(r'## 🤖 AGENTS UTILIZED.*?\*', '', formatted_response, flags=re.DOTALL)
        formatted_response = re.sub(r'\*\*🔍 RESEARCH METHODOLOGY\*\*.*?\*\*⚖️ LEGAL FRAMEWORK\*\*', '**⚖️ LEGAL FRAMEWORK**', formatted_response, flags=re.DOTALL)
        formatted_response = re.sub(r'\*\*🔍 RESEARCH METHODOLOGY\*\*.*?\*\*📚 CASE PRECEDENTS\*\*', '**📚 CASE PRECEDENTS**', formatted_response, flags=re.DOTALL)
        
        # Remove any context-related text
        formatted_response = re.sub(r'Context:.*?\n', '', formatted_response, flags=re.DOTALL)
        formatted_response = re.sub(r'Follow-up.*?\n', '', formatted_response, flags=re.DOTALL)
        formatted_response = re.sub(r'Previous.*?\n', '', formatted_response, flags=re.DOTALL)
        
        # Remove memory context footer
        formatted_response = re.sub(r'---.*?💡 \*\*Memory Context\*\*.*?📊 \*\*Quality Score\*\*.*?\*', '', formatted_response, flags=re.DOTALL)
        
        # Remove conversation context section
        formatted_response = re.sub(r'## CONVERSATION CONTEXT.*?previous analysis\.', '', formatted_response, flags=re.DOTALL)
        
        # Remove memory-enhanced insights section
        formatted_response = re.sub(r'## MEMORY-ENHANCED INSIGHTS.*?legal strategy\.', '', formatted_response, flags=re.DOTALL)
        
        # Clean up any remaining ugly formatting
        formatted_response = re.sub(r'\*\*Next Steps\*\*:.*?---', '', formatted_response, flags=re.DOTALL)
        formatted_response = re.sub(r'---\s*$', '', formatted_response)
        
        # Ensure proper markdown formatting for frontend
        formatted_response = formatted_response.strip()
        
        # Add a clean header if not present
        if not formatted_response.startswith('#'):
            formatted_response = f"# Legal Research Analysis\n\n{formatted_response}"
        
        # Remove any remaining context indicators
        formatted_response = re.sub(r'Building on.*?discussion.*?\n', '', formatted_response, flags=re.IGNORECASE)
        formatted_response = re.sub(r'Following up.*?\n', '', formatted_response, flags=re.IGNORECASE)
        formatted_response = re.sub(r'As discussed.*?\n', '', formatted_response, flags=re.IGNORECASE)
        
        # Enhance formatting for better frontend display
        formatted_response = self._enhance_markdown_formatting(formatted_response)
        
        return formatted_response
    
    def _enhance_markdown_formatting(self, content: str) -> str:
        """Enhance markdown formatting for better frontend display"""
        
        # Remove any lines about law retrievers or unnecessary text
        content = re.sub(r'If you need the verbatim text.*?Let me know which article.*?', '', content, flags=re.DOTALL)
        content = re.sub(r'I can retrieve it using.*?', '', content, flags=re.DOTALL)
        
        # Remove # symbols from headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Add proper spacing around headers
        content = re.sub(r'(\*\*[^*]+\*\*)(\n)', r'\1\2\n', content)
        
        # Enhance lists
        content = re.sub(r'^\s*[-*]\s+', '• ', content, flags=re.MULTILINE)
        
        # Add emphasis to important sections
        content = re.sub(r'(\*\*[^*]+\*\*:)', r'**\1**', content)
        
        # Add proper spacing for sections
        content = re.sub(r'(\*\*[^*]+\*\*)(\n)', r'\n\1\n', content)
        
        # Enhance links
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'🔗 [\1](\2)', content)
        
        # Add icons to sections (now using ** format instead of ##)
        content = re.sub(r'\*\*📋 QUERY ANALYSIS\*\*', r'**📋 QUERY ANALYSIS**', content)
        content = re.sub(r'\*\*🔍 RESEARCH METHODOLOGY\*\*', r'**🔍 RESEARCH METHODOLOGY**', content)
        content = re.sub(r'\*\*⚖️ LEGAL FRAMEWORK\*\*', r'**⚖️ LEGAL FRAMEWORK**', content)
        content = re.sub(r'\*\*📚 CASE PRECEDENTS\*\*', r'**📚 CASE PRECEDENTS**', content)
        content = re.sub(r'\*\*💼 LEGAL ARGUMENTS & STRATEGY\*\*', r'**💼 LEGAL ARGUMENTS & STRATEGY**', content)
        content = re.sub(r'\*\*🎯 CASE ASSESSMENT\*\*', r'**🎯 CASE ASSESSMENT**', content)
        content = re.sub(r'\*\*📋 ACTIONABLE STEPS\*\*', r'**📋 ACTIONABLE STEPS**', content)
        content = re.sub(r'\*\*🔗 ADDITIONAL RESOURCES\*\*', r'**🔗 ADDITIONAL RESOURCES**', content)
        content = re.sub(r'\*\*📊 QUALITY ASSURANCE\*\*', r'**📊 QUALITY ASSURANCE**', content)
        content = re.sub(r'\*\*📝 EXECUTIVE SUMMARY\*\*', r'**📝 EXECUTIVE SUMMARY**', content)
        content = re.sub(r'\*\*🔗 IMPORTANT LINKS\*\*', r'**🔗 IMPORTANT LINKS**', content)
        
        # Add dividers between major sections
        content = re.sub(r'(\*\*[^*]+\*\*)(\n)(\*\*[^*]+\*\*)', r'\1\2\n---\n\3', content)
        
        # Clean up multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure proper spacing around the summary section
        content = re.sub(r'(\*\*📝 EXECUTIVE SUMMARY\*\*)(\n)', r'\1\2\n', content)
        
        return content
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        total = self.stats['total_queries']
        success_rate = (self.stats['successful_queries'] / total * 100) if total > 0 else 0
        
        return {
            'total_queries': total,
            'successful_queries': self.stats['successful_queries'],
            'failed_queries': self.stats['failed_queries'],
            'success_rate': f"{success_rate:.1f}%",
            'average_response_time': f"{self.stats['average_response_time']:.2f}s",
            'agents_called': self.stats['agents_called'],
            'conversation_memory': len(self.conversation_history),
            'memory_context': "Active" if self.conversation_history else "None"
        }
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history = []
        self.last_analysis_type = None
        self.last_legal_issues = []
        self.last_cases = []
        self.last_laws = []
        logger.info("Conversation memory cleared")

if __name__ == "__main__":
    # Test the legal research system
    test_queries = [
        "What are the fundamental rights in Indian Constitution?",
        "What about the right to education?",
        "And what are the remedies for violation of these rights?"
    ]
    
    print("=== Testing Legal Research System ===")
    
    # Create an instance for testing
    legal_strategist = LegalStrategist()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        
        result = legal_strategist.run_with_monitoring(query)
        
        if result['status'] == 'success':
            print(f"✅ Research completed successfully!")
            print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
            print(f"🔄 Attempts: {result['attempts']}")
            print(f"🤖 Agents called: {result['agents_called']}")
            print(f"🧠 Memory context: {result['memory_context']} conversations")
            print(f"\n📋 Response preview:")
            print(result['content'][:500] + "...")
        else:
            print(f"❌ Research failed: {result['error']}")
    
    # Show statistics
    stats = legal_strategist.get_statistics()
    print(f"\n📈 System Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
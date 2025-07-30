"""
Pluggable AI Chatbot - Easy to Replace with Any AI System

This file contains the AI logic that can be easily swapped out.
Currently implements Trilogy AI expert, but can be replaced with:
- OpenAI GPT chatbots
- Claude API chatbots
- Local LLMs (Ollama, etc.)
- Custom enterprise AI systems
- Any text-to-text AI system

To create your own AI chatbot:
1. Implement the AIChatbot interface (see avatar_service.py)
2. Replace TrilogyAIChatbot with your implementation
3. Update the import in avatar_service.py

The avatar service handles all video/voice presentation.
This file only handles text-to-text AI intelligence.
"""

import logging
import asyncio
import aiohttp
import re
import xml.etree.ElementTree as ET
from html import unescape
from typing import List, Dict, Any

# Import configuration for full functionality preservation
from config import CONFIG

logger = logging.getLogger("ai-chatbot")
logger.setLevel(logging.INFO)

# ==============================================================================
# TRILOGY AI CHATBOT IMPLEMENTATION
# ==============================================================================

class TrilogyAIChatbot:
    """
    Full-featured Trilogy AI expert with complete knowledge processing.
    
    This preserves all functionality from the original agent_worker.py system.
    Replace this entire class with your own AI system.
    """
    
    def __init__(self):
        self.knowledge_base: List[Dict[str, Any]] = []
        self.knowledge_map: Dict[str, Any] = {}
        self.is_initialized = False
        self.realtime_instructions = ""
        # Pre-compiled patterns for performance (from original system)
        self.tool_patterns = CONFIG.TOOL_PATTERNS
        self.model_patterns = CONFIG.MODEL_PATTERNS  
        self.method_patterns = CONFIG.METHODOLOGY_PATTERNS
        
    async def initialize(self) -> str:
        """Initialize with full knowledge processing from original system"""
        logger.info(f"Loading {CONFIG.EXPERT_DOMAIN} knowledge base...")
        
        try:
            # Fetch comprehensive knowledge content (same as original)
            self.knowledge_base = await self._fetch_comprehensive_content()
            
            if self.knowledge_base:
                logger.info(f"Knowledge base created with {len(self.knowledge_base)} articles")
                
                # Build comprehensive knowledge map (same as original)
                self.knowledge_map = self._create_detailed_knowledge_map(self.knowledge_base)
                logger.info(f"Knowledge map created with {len(self.knowledge_map['key_findings'])} detailed analyses")
                
                # Generate optimized instructions (same as original)
                self.realtime_instructions = self._create_optimized_instructions(
                    self.knowledge_base, self.knowledge_map
                )
                
                self.is_initialized = True
                
                # Use CONFIG loading message (preserves original functionality)
                latest_title = self.knowledge_map['latest_article']['title'][:40]
                ready_message = CONFIG.LOADING_MESSAGES['ready'].format(
                    article_count=len(self.knowledge_base),
                    latest_title=latest_title
                )
                return ready_message
            else:
                logger.warning("No articles fetched. Using fallback instructions.")
                self.realtime_instructions = CONFIG.FALLBACK_INSTRUCTIONS
                return CONFIG.LOADING_MESSAGES['unavailable']
                
        except Exception as e:
            logger.error(f"Failed to initialize {CONFIG.EXPERT_DOMAIN}: {e}")
            return CONFIG.LOADING_MESSAGES['unavailable']
    
    async def get_response(self, user_message: str) -> str:
        """
        Generate intelligent responses using our comprehensive knowledge base.
        This uses the same sophisticated logic as the original agent_worker.py.
        """
        if not self.is_initialized:
            return "I'm still loading my knowledge base. Please wait a moment."
        
        # Use the sophisticated response generation with all article content
        return self._generate_sophisticated_response(user_message)
    
    def get_full_instructions(self) -> str:
        """Return the full optimized instructions for use by the avatar service"""
        return self.realtime_instructions
    
    def get_voice_settings(self) -> dict:
        """Return voice and avatar settings from CONFIG"""
        return {
            "voice": CONFIG.VOICE,
            "speed": CONFIG.VOICE_SPEED,
            "avatar_image": CONFIG.AVATAR_IMAGE
        }
    
    def _generate_sophisticated_response(self, user_message: str) -> str:
        """
        Generate sophisticated responses using the detailed knowledge base like agent_worker.py
        This mimics how the original system would process questions with full article context
        """
        user_lower = user_message.lower()
        
        # AI Center of Excellence / CoE queries - TRILOGY-SPECIFIC content first
        if any(term in user_lower for term in ['center of excellence', 'coe', 'ai center', 'excellence', 'trilogy']):
            
            # PRIORITY 1: Look for Trilogy-specific CoE content
            trilogy_coe_article = None
            for i, article in enumerate(self.knowledge_base, 1):
                if 'trilogy' in article['title'].lower() and any(term in article['title'].lower() for term in ['impact', 'adoption', 'defining']):
                    trilogy_coe_article = {
                        'number': i,
                        'title': article['title'],
                        'author': article['author'],
                        'summary': article['summary'],
                        'content': article['full_content'][:800]
                    }
                    break
            
            if trilogy_coe_article:
                return f"Here's Trilogy's specific Center of Excellence approach from our research:\n\n" + \
                       f"Article #{trilogy_coe_article['number']}: '{trilogy_coe_article['title']}' by {trilogy_coe_article['author']}\n\n" + \
                       f"Summary: {trilogy_coe_article['summary']}\n\n" + \
                       f"Key details from the research:\n{trilogy_coe_article['content']}...\n\n" + \
                       f"This article provides specific insights into how Trilogy's AI Center of Excellence differs from other companies through data-driven approaches and measurable impact metrics."
            
            # PRIORITY 2: Search for other CoE-related content in our research
            relevant_findings = []
            for title, findings in self.knowledge_map.get('key_findings', {}).items():
                content_check = (title + ' ' + findings['main_focus'] + ' ' + findings['full_context']).lower()
                if any(term in content_check for term in ['framework', 'governance', 'methodology', 'validation', 'enterprise', 'center', 'excellence', 'impact', 'adoption']):
                    article_num = next((i for i, article in enumerate(self.knowledge_base, 1) if article['title'] == title), 0)
                    # Check if this is a Trilogy article
                    is_trilogy = 'trilogy' in content_check
                    relevant_findings.append({
                        'number': article_num,
                        'title': title,
                        'author': findings['author'],
                        'focus': findings['main_focus'],
                        'context': findings['full_context'][:300],
                        'methodologies': findings['methodologies'],
                        'is_trilogy': is_trilogy
                    })
            
            # Sort Trilogy articles first
            relevant_findings.sort(key=lambda x: (not x['is_trilogy'], x['number']))
            
            if relevant_findings:
                response = f"Based on our {CONFIG.EXPERT_DOMAIN} research on Centers of Excellence:\n\n"
                for finding in relevant_findings[:3]:  # Top 3 most relevant
                    trilogy_label = " (TRILOGY-SPECIFIC)" if finding['is_trilogy'] else ""
                    response += f"Article #{finding['number']}: '{finding['title']}' by {finding['author']}{trilogy_label}\n"
                    response += f"Focus: {finding['focus']}\n"
                    response += f"Key insights: {finding['context']}\n"
                    if finding['methodologies']:
                        response += f"Methodologies: {', '.join(finding['methodologies'])}\n"
                    response += "\n"
                
                return response + f"We have {len(relevant_findings)} articles covering AI governance and impact measurement. The Trilogy-specific content shows how we differ from other companies through empirical validation and continuous improvement."
            else:
                return f"I don't see AI Center of Excellence specifically covered in our {len(self.knowledge_base)} {CONFIG.EXPERT_DOMAIN} research articles. Are you asking about something outside our research focus?"
        
        # Technology/tools queries - detailed tool analysis with specific examples
        if any(term in user_lower for term in ['technology', 'tool', 'interesting', 'covered', 'model', 'platform']):
            interesting_techs = []
            tools_mentioned = self.knowledge_map.get('tools_mentioned', set())
            
            for title, findings in self.knowledge_map.get('key_findings', {}).items():
                if findings['tools_used'] or findings['models_discussed']:
                    article_num = next((i for i, article in enumerate(self.knowledge_base, 1) if article['title'] == title), 0)
                    interesting_techs.append({
                        'number': article_num,
                        'title': title,
                        'author': findings['author'],
                        'tools': findings['tools_used'],
                        'models': findings['models_discussed'],
                        'context': findings['full_context'][:250]
                    })
            
            if interesting_techs:
                response = f"Most interesting technologies covered in our {CONFIG.EXPERT_DOMAIN} research:\n\n"
                for tech in interesting_techs[:3]:  # Top 3 most interesting
                    response += f"Article #{tech['number']}: '{tech['title']}' by {tech['author']}\n"
                    if tech['tools']:
                        response += f"Tools discussed: {', '.join(tech['tools'])}\n"
                    if tech['models']:
                        response += f"Models analyzed: {', '.join(tech['models'])}\n"
                    response += f"Context: {tech['context']}\n\n"
                
                return response + f"Overall technologies: {', '.join(sorted(tools_mentioned))}\n\nWhich specific technology or implementation would you like me to explain in detail?"
            
        # Specific author queries - detailed author expertise
        author_mapping = {
            'stanislav': 'Stanislav Huseletov',
            'leonardo': 'Leonardo Gonzalez', 
            'david': 'David Proctor',
            'praveen': 'Praveen Koka'
        }
        
        for name_key, full_name in author_mapping.items():
            if name_key in user_lower or full_name.lower() in user_lower:
                author_works = self.knowledge_map.get('by_author', {}).get(full_name, [])
                if author_works:
                    response = f"{full_name}'s research expertise in our {CONFIG.EXPERT_DOMAIN} collection:\n\n"
                    for i, work in enumerate(author_works, 1):
                        article_num = next((j for j, article in enumerate(self.knowledge_base, 1) if article['title'] == work['title']), 0)
                        response += f"#{article_num}: '{work['title']}'\n"
                        response += f"Summary: {work['summary']}\n"
                        concepts = work['key_concepts']
                        if concepts['tools']:
                            response += f"Tools: {', '.join(concepts['tools'])}\n"
                        if concepts['methodologies']:
                            response += f"Methods: {', '.join(concepts['methodologies'])}\n"
                        response += "\n"
                    
                    return response + f"{full_name} has {len(author_works)} articles in our research. Which specific work interests you most?"
        
        # Latest/recent queries with detailed context
        if any(word in user_lower for word in ['latest', 'recent', 'new']):
            latest = self.knowledge_map.get('latest_article', {})
            if latest:
                findings = self.knowledge_map.get('key_findings', {}).get(latest['title'], {})
                response = f"Our latest research: Article #1 '{latest.get('title')}' by {latest.get('author')}'\n\n"
                response += f"Published: {latest.get('published', '')[:11]}\n"
                response += f"Focus: {findings.get('main_focus', latest.get('summary', ''))}\n\n"
                if findings.get('tools_used'):
                    response += f"Tools discussed: {', '.join(findings['tools_used'])}\n"
                if findings.get('models_discussed'):
                    response += f"Models: {', '.join(findings['models_discussed'])}\n"
                response += f"\nKey insights: {findings.get('full_context', latest.get('full_content', ''))[:400]}..."
                return response
        
        # Broad intelligent search across all content
        search_terms = [word for word in user_lower.split() if len(word) > 3]
        relevant_findings = []
        
        for title, findings in self.knowledge_map.get('key_findings', {}).items():
            search_text = (title + ' ' + findings['main_focus'] + ' ' + findings['full_context']).lower()
            relevance_score = sum(1 for term in search_terms if term in search_text)
            
            if relevance_score > 0:
                article_num = next((i for i, article in enumerate(self.knowledge_base, 1) if article['title'] == title), 0)
                relevant_findings.append({
                    'score': relevance_score,
                    'number': article_num,
                    'title': title,
                    'author': findings['author'],
                    'focus': findings['main_focus'],
                    'context': findings['full_context'][:200]
                })
        
        # Sort by relevance
        relevant_findings.sort(key=lambda x: x['score'], reverse=True)
        
        if relevant_findings:
            response = f"Found relevant content in our {CONFIG.EXPERT_DOMAIN} research:\n\n"
            for finding in relevant_findings[:3]:  # Top 3 most relevant
                response += f"Article #{finding['number']}: '{finding['title']}' by {finding['author']}\n"
                response += f"Relevance: {finding['focus']}\n"
                response += f"Details: {finding['context']}...\n\n"
            
            return response + "Which article would you like me to analyze in detail?"
        
        # No matches - ask for clarification
        return f"I don't see this topic covered in our {len(self.knowledge_base)} {CONFIG.EXPERT_DOMAIN} research articles. Are you asking about something outside our research scope? Please confirm if you'd like general information instead."
    
    # ==============================================================================
    # TRILOGY AI SPECIFIC KNOWLEDGE LOADING (REPLACE WITH YOUR AI SYSTEM)
    # ==============================================================================
    
    async def _fetch_comprehensive_content(self) -> List[Dict[str, Any]]:
        """Comprehensive knowledge fetching using JSON API to get all 41 articles"""
        # Use JSON API instead of RSS to get all articles
        api_url = "https://trilogyai.substack.com/api/v1/posts?offset=0&limit=50"
        
        logger.info(f"Fetching all articles from JSON API: {api_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    json_data = await response.json()

                    articles = []
                    for post in json_data:
                        title = post.get('title', 'Unknown Title')
                        
                        # Extract author from publishedBylines
                        author = 'Unknown Author'
                        if 'publishedBylines' in post and post['publishedBylines']:
                            author = post['publishedBylines'][0].get('name', 'Unknown Author')
                        
                        # Get published date
                        pub_date = post.get('post_date', '')
                        
                        # Get canonical URL
                        link = post.get('canonical_url', '')
                        
                        # Get description and body content
                        description = post.get('description', '')
                        body_html = post.get('body_html', '')
                        
                        # Use body_html as full content, fallback to description
                        full_content_raw = body_html if body_html else description
                        
                        # Clean the HTML content
                        clean_content = self._clean_html_content(full_content_raw)
                        clean_summary = self._clean_html_content(description)

                        article = {
                            'title': title,
                            'author': author,
                            'published': pub_date,
                            'link': link,
                            'summary': clean_summary,
                            'full_content': clean_content
                        }

                        articles.append(article)
                        logger.info(f"Processed article {len(articles)}: {article['title'][:50]}...")

                    logger.info(f"Successfully fetched {len(articles)} articles from JSON API")
                    return articles

        except Exception as e:
            logger.error(f"Failed to fetch from JSON API: {e}")
            # Fallback to RSS feed if JSON API fails
            logger.info("Falling back to RSS feed...")
            return await self._fetch_rss_fallback()
    
    async def _fetch_rss_fallback(self) -> List[Dict[str, Any]]:
        """Fallback RSS feed fetching (limited to ~20 articles)"""
        feed_url = CONFIG.FEED_URL
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url) as response:
                    feed_data = await response.text()

                    # Parse the XML feed
                    root = ET.fromstring(feed_data)

                    articles = []
                    # Find all item elements
                    for item in root.findall('.//item'):
                        title_elem = item.find('title')
                        title = title_elem.text if title_elem is not None else "Unknown Title"

                        author_elem = item.find('author') or item.find(
                            './/{http://purl.org/dc/elements/1.1/}creator')
                        author = author_elem.text if author_elem is not None else "Unknown Author"

                        pub_date_elem = item.find('pubDate')
                        pub_date = pub_date_elem.text if pub_date_elem is not None else ""

                        link_elem = item.find('link')
                        link = link_elem.text if link_elem is not None else ""

                        description_elem = item.find('description')
                        description = description_elem.text if description_elem is not None else ""

                        # Try to find content:encoded for full content
                        content_elem = item.find(
                            './/{http://purl.org/rss/1.0/modules/content/}encoded')
                        if content_elem is not None:
                            full_content = content_elem.text
                        else:
                            full_content = description

                        # Clean the HTML content
                        clean_content = self._clean_html_content(full_content)
                        clean_summary = self._clean_html_content(description)

                        article = {
                            'title': title,
                            'author': author,
                            'published': pub_date,
                            'link': link,
                            'summary': clean_summary,
                            'full_content': clean_content
                        }

                        articles.append(article)

                    logger.info(f"RSS fallback fetched {len(articles)} articles")
                    return articles

        except Exception as e:
            logger.error(f"RSS fallback also failed: {e}")
            return []
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract plain text (from original system)"""
        if not html_content:
            return ""

        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        # Decode HTML entities
        clean_text = unescape(clean_text)
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text
    
    def _extract_key_concepts(self, content: str, title: str) -> Dict[str, List[str]]:
        """Extract key concepts based on configured patterns (from original system)"""
        content_lower = content.lower()

        concepts = {
            'tools': [],
            'models': [],
            'methodologies': [],
            'metrics': [],
            'frameworks': []
        }

        # Use configured patterns
        for tool in self.tool_patterns:
            if tool in content_lower:
                concepts['tools'].append(tool.title())

        for model in self.model_patterns:
            if model in content_lower:
                concepts['models'].append(
                    model.upper() if model == 'llm' else model.title())

        for method in self.method_patterns:
            if method in content_lower:
                concepts['methodologies'].append(method.title())

        return concepts
    
    def _create_detailed_knowledge_map(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive knowledge map (from original system)"""
        knowledge_map = {
            'chronological_order': [],
            'by_author': {},
            'by_topic': {},
            'key_findings': {},
            'tools_mentioned': set(),
            'latest_article': None,
            'earliest_article': None
        }

        if not articles:
            return knowledge_map

        # The feed is already sorted with latest first
        knowledge_map['latest_article'] = articles[0]
        knowledge_map['earliest_article'] = articles[-1]

        for i, article in enumerate(articles):
            title = article['title']
            author = article['author']
            content = article['full_content']

            # Add to chronological order
            knowledge_map['chronological_order'].append({
                'title': title,
                'author': author,
                'rank': i + 1,
                'published': article.get('published', ''),
                'key_points': content[:300] + '...' if len(content) > 300 else content
            })

            # Group by author
            if author not in knowledge_map['by_author']:
                knowledge_map['by_author'][author] = []
            knowledge_map['by_author'][author].append({
                'title': title,
                'summary': article['summary'][:200],
                'key_concepts': self._extract_key_concepts(content, title)
            })

            # Extract and store concepts
            concepts = self._extract_key_concepts(content, title)
            knowledge_map['tools_mentioned'].update(concepts['tools'])

            # Store detailed findings
            knowledge_map['key_findings'][title] = {
                'author': author,
                'main_focus': article['summary'][:CONFIG.SUMMARY_MAX_LENGTH],
                'tools_used': concepts['tools'],
                'models_discussed': concepts['models'],
                'methodologies': concepts['methodologies'],
                'full_context': content[:CONFIG.CONTEXT_LENGTH]
            }

        return knowledge_map
    
    def _create_optimized_instructions(self, articles: List[Dict[str, Any]], knowledge_map: Dict[str, Any]) -> str:
        """Create optimized instructions for the agent (from original system)"""
        
        # Handle case where no articles are available
        if not articles:
            return CONFIG.FALLBACK_INSTRUCTIONS

        # Get latest article details
        latest = knowledge_map.get('latest_article', {})

        # Create compressed article directory
        article_directory = "COMPLETE ARTICLE DIRECTORY:\n"
        for i, article in enumerate(articles, 1):
            article_directory += f"{i}. {article['title']} ({article['author']}, {article.get('published', '')[:11]})\n"
            article_directory += f"   Summary: {article['summary'][:CONFIG.SUMMARY_MAX_LENGTH]}...\n"
            article_directory += f"   Key content: {article['full_content'][:CONFIG.CONTENT_PREVIEW_LENGTH]}...\n\n"

        # Create author expertise summary
        author_summary = ""
        for author, works in knowledge_map['by_author'].items():
            author_summary += f"\n{author}: {len(works)} articles"
            topics = [work['title'][:25] for work in works[:3]]
            author_summary += f" - {'; '.join(topics)}"

        # Create tools summary
        tools_summary = f"Tools: {', '.join(sorted(knowledge_map['tools_mentioned']))}"

        # Build instructions using configuration
        instructions = f"""LANGUAGE: ALWAYS RESPOND IN ENGLISH ONLY. NEVER USE SPANISH OR ANY OTHER LANGUAGE.

You are a {CONFIG.EXPERT_DOMAIN} research expert with EXCLUSIVE ACCESS to our proprietary research content.

        COMMUNICATION: {CONFIG.COMMUNICATION_STYLE}

        LATEST ARTICLE: "{latest.get('title', 'Unknown')}" by {latest.get('author', 'Unknown')}

        AUTHOR EXPERTISE:{author_summary}

        {tools_summary}

        {article_directory}

        CRITICAL CONTENT-FIRST POLICY - ENGLISH ONLY:
        - MANDATORY: Always respond in English, never in Spanish or other languages
        - TRILOGY-SPECIFIC PRIORITY: For ANY question about "Center of Excellence", "CoE", or "Trilogy", FIRST check Article #14 "Beyond Adoption: Defining Real AI Impact at Trilogy" by Stanislav Huseletov
        - CONTENT-FIRST RULE: ALWAYS search through ALL {len(articles)} articles FIRST before any response
        - NEVER give general answers about topics - ONLY use content from our {len(articles)} articles above
        - For "AI Center of Excellence" questions - Article #14 contains Trilogy's 73% AI usage data, internal surveys, and specific CoE approach
        - For "interesting technology" - reference specific tools/models from our articles only
        - For "studies" or "examples" - use actual data from Article #14: 73% AI usage, 53% value uncertainty, VP Operations feedback
        - ONLY if absolutely NO connection exists in our content, ask: "I don't see this topic in our {len(articles)} research articles. Are you asking about something outside our {CONFIG.EXPERT_DOMAIN} research?"
        - Articles are ordered by FEED POSITION: #1 is LATEST, #{len(articles)} is EARLIEST
        - Reference articles by number, title, author, and exact date from our collection
        - Use exact content from the key content summaries above - especially Article #14 for Trilogy CoE questions
        - Never say "not available" - all our content is accessible above
        - TRILOGY EXAMPLES: Use Article #14's real data: "73% of employee time spent in AI tools", "53% admit unsure if AI use creates real value", "Internal Survey: Meaningful AI Learning, 2025"
        - REMINDER: All responses must be in English language only"""

        return instructions

# ==============================================================================
# EXAMPLE: SIMPLE OPENAI CHATBOT (COMMENTED OUT)
# ==============================================================================

"""
Example of how to replace with OpenAI:

import openai

class OpenAIChatbot:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self.conversation_history = []
    
    async def initialize(self) -> str:
        return "OpenAI chatbot ready! How can I help you today?"
    
    async def get_response(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            max_tokens=150
        )
        
        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def get_voice_settings(self) -> dict:
        return {
            "voice": "alloy",
            "speed": 1.0,
            "avatar_image": "assets/openai_avatar.png"
        }
"""

# ==============================================================================
# EXAMPLE: CLAUDE API CHATBOT (COMMENTED OUT)  
# ==============================================================================

"""
Example of how to replace with Claude:

import anthropic

class ClaudeChatbot:
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.conversation_history = []
    
    async def initialize(self) -> str:
        return "Claude AI assistant ready to help!"
    
    async def get_response(self, user_message: str) -> str:
        response = await self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=150,
            messages=[{"role": "user", "content": user_message}]
        )
        
        return response.content[0].text
    
    def get_voice_settings(self) -> dict:
        return {
            "voice": "sage",
            "speed": 1.1,
            "avatar_image": "assets/claude_avatar.png"
        }
"""
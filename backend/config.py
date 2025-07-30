# ==============================================================================
# KNOWLEDGE SOURCE CONFIGURATION
# ==============================================================================
# This file contains all the knowledge source-specific settings.
# Developers can modify this file to plug in their own knowledge repositories.
# ==============================================================================

from typing import List

class KnowledgeSourceConfig:
    """Configuration for knowledge source and domain expertise"""
    
    # ========================================
    # KNOWLEDGE SOURCE SETTINGS
    # ========================================
    
    # RSS/Feed URL to fetch content from
    FEED_URL: str = "https://trilogyai.substack.com/feed"
    
    # Expert domain name (used in instructions and greetings)
    EXPERT_DOMAIN: str = "Trilogy AI"
    
    # Voice and personality settings
    VOICE: str = "ash"  # Options: alloy, ash, ballad, coral, echo, sage, shimmer, verse
    VOICE_SPEED: float = 1.2  # 0.25 to 4.0
    
    # Avatar image path (relative to backend directory)
    AVATAR_IMAGE: str = "assets/stan.png"
    
    # ========================================
    # CONCEPT EXTRACTION PATTERNS
    # ========================================
    # Customize these patterns to extract relevant concepts from your content
    
    TOOL_PATTERNS: List[str] = [
        'openevolve', 'firecrawl', 'postgresql',
        'n8n', 'airtable', 'deepmind', 'google', 'livekit'
    ]
    
    MODEL_PATTERNS: List[str] = [
        'qwen', 'gpt', 'claude', 'llm', 'grok', 'kimi', 'deepagent'
    ]
    
    METHODOLOGY_PATTERNS: List[str] = [
        'crawl', 'algo trading', 'multi-model',
        'iterative', 'automation', 'discovery', 'validation'
    ]
    
    # ========================================
    # AGENT PERSONALITY & INSTRUCTIONS
    # ========================================
    
    # Base personality for the agent
    COMMUNICATION_STYLE: str = "ENGLISH ONLY: Always respond in English language only. Reserved, measured, authoritative. Speak with deliberate pace and minimal enthusiasm. Reference specific details from articles when asked. Never use Spanish or other languages."
    
    # Initial loading messages
    LOADING_MESSAGES = {
        "initializing": f"{EXPERT_DOMAIN} expert initializing. Loading comprehensive knowledge base...",
        "processing": "Processing research articles...",
        "unavailable": "Knowledge base temporarily unavailable. I can still assist with general AI research questions.",
        "ready": "Knowledge base loaded. I have comprehensive access to {article_count} research articles, including the latest on {latest_title}. What would you like to know?"
    }
    
    # Fallback instructions when no content is available
    FALLBACK_INSTRUCTIONS: str = f"You are a {EXPERT_DOMAIN} research expert. The knowledge base is currently unavailable, but you can still provide general AI research insights."
    
    # ========================================
    # CONTENT PROCESSING SETTINGS  
    # ========================================
    
    # Maximum content length for article summaries
    SUMMARY_MAX_LENGTH: int = 100
    CONTENT_PREVIEW_LENGTH: int = 200
    CONTEXT_LENGTH: int = 1000
    
    # Number of recent articles to highlight
    RECENT_ARTICLES_COUNT: int = 13


# ==============================================================================
# ACTIVE CONFIGURATION
# ==============================================================================
# Change this line to switch between different knowledge sources
# ==============================================================================

# Use Trilogy AI configuration (default)
CONFIG = KnowledgeSourceConfig()

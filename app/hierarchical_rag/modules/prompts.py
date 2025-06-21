from typing import Any
from app.core import PromptProcessor, PromptPayload, PromptTemplate

from ..models.models import QAPairs, TagList

# Template definitions for various prompt-based tasks in medical document processing
TEMPLATES = {
    "page_questions": PromptTemplate(
        name="page_questions",
        instructions=(
            "You are a clinical assistant tasked with extracting important question-answer "
            "pairs from medical documents to populate a structured database."
        ),
        prompt="""
            You are given the following page from a medical document:
            {page_text}
            
            Based on the content, generate a concise list of high-priority questions and their corresponding answers. 
            Each question-answer pair should be clear and specific.
        """
        ),
    "body_tags_page": PromptTemplate(
        name="body_tags_page",
        instructions=(
            "You are a clinical assistant responsible for tagging pages from medical documents "
            "with relevant body parts mentioned in the text."
            "Each tag must be only single word"
        ),
        prompt="""
            You are given the following page from a medical document
            {page_text}

            Extract a list of relevant anatomical structures or body parts mentioned on this page. 
            Include only specific terms that refer to organs, tissues, systems (e.g., cardiovascular), or regions of the body.
            Return the output as a simple comma-separated list of tags (e.g., lungs, heart, nervous system).
        """
        ),
    "body_tags_query": PromptTemplate(
        name="body_tags_query",
        instructions=(
            "You are a clinical assistant helping to categorize user queries by identifying relevant body parts."
        ),
        prompt="""
            You are given the following user query:
            {query}
            
            Identify all relevant anatomical structures or body parts mentioned or implied in the query. 
            Return them as a comma-separated list of single-word tags only (e.g., heart, liver, spine).
            Avoid multi-word phrases. Focus on specific organs, systems, or body regions mentioned directly or indirectly.
        """
        ),
    "questions_query": PromptTemplate(
        name="questions_query",
        instructions=(
            "You are a clinical assistant tasked with generating important questions from a user query."
        ),
        prompt="""
            You are given the following user query:
            {query}
            
            Create a list of {n_questions} most likely questions this query is related to.
        """
        )
}

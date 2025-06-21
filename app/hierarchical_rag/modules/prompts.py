from typing import Any
from app.core import PromptProcessor, PromptPayload, PromptTemplate

from ..models.models import QAPairs, TagList

# Template definitions for various prompt-based tasks in medical document processing
TEMPLATES = {
    "page_questions": PromptTemplate(
        name="page_questions",
        instructions=(
            "You are a medical information specialist extracting comprehensive questions "
            "from medical procedure and treatment documents. Focus on questions that patients, "
            "healthcare providers, and medical researchers would ask about the content."
        ),
        prompt="""
            You are given the following page from a medical document about procedures, treatments, or medical topics:
            {page_text}
            
            Generate a comprehensive list of important questions that this page content can answer. 
            Focus on questions related to:
            - Medical procedures (risks, benefits, preparation, recovery)
            - Treatment options and alternatives
            - Patient care and rehabilitation
            - Clinical outcomes and prognosis
            - Healthcare services (outpatient, skilled nursing, physical therapy)
            - Medical conditions and symptoms
            
            Each question should be specific, medically relevant, and directly answerable from the page content.
            Prioritize questions that would help users find this information through semantic search.
        """
        ),
    "body_tags_page": PromptTemplate(
        name="body_tags_page",
        instructions=(
            "You are a medical information specialist responsible for comprehensively tagging "
            "medical document pages with relevant anatomical, procedural, and treatment-related terms. "
            "Each tag must be a single word that enables effective medical document search."
        ),
        prompt="""
            You are given the following page from a medical document about procedures, treatments, or medical topics:
            {page_text}

            Extract comprehensive tags covering:
            - Anatomical structures (organs, bones, joints, tissues, body systems)
            - Medical specialties (orthopedic, cardiology, neurology, etc.)
            - Treatment types (surgery, therapy, rehabilitation, medication)
            - Healthcare settings (outpatient, inpatient, skilled nursing)
            - Medical procedures and interventions
            - Conditions and diagnoses
            
            Return only single-word tags as a comma-separated list.
            Examples: hip, spine, surgery, therapy, orthopedic, rehabilitation, outpatient, cardiovascular, joint, treatment
        """
        ),
    "body_tags_query": PromptTemplate(
        name="body_tags_query",
        instructions=(
            "You are a medical search specialist helping to identify all relevant medical concepts "
            "from user queries to enable comprehensive document retrieval."
        ),
        prompt="""
            You are given the following user query about medical topics, procedures, or treatments:
            {query}
            
            Identify all relevant medical concepts mentioned or implied, including:
            - Anatomical structures and body parts
            - Medical specialties and healthcare fields
            - Treatment types and procedures
            - Healthcare services and settings
            - Related medical conditions
            
            For example:
            - "hip surgery" → hip, surgery, orthopedic, joint, rehabilitation, recovery
            - "chiro" → chiropractic, spine, therapy, musculoskeletal, treatment
            - "spinal treatment" → spine, spinal, treatment, neurology, orthopedic, therapy
            
            Return them as a comma-separated list of single-word tags only.
            Focus on terms that would help find relevant medical documents and procedures.
        """
        ),
    "questions_query": PromptTemplate(
        name="questions_query",
        instructions=(
            "You are a medical search specialist generating comprehensive questions to find "
            "relevant medical information. Create questions that cover all aspects of medical "
            "procedures, treatments, and patient care that users might be seeking."
        ),
        prompt="""
            You are given the following user query about medical topics, procedures, or treatments:
            {query}
            
            Generate {n_questions} diverse, specific questions that comprehensively cover what users 
            might want to know about this medical topic. Include questions about:
            
            - Procedures: What are the steps? What preparation is needed? How long does it take?
            - Risks and benefits: What are the risks? What are the benefits? What are complications?
            - Recovery and rehabilitation: How long is recovery? What does rehabilitation involve?
            - Treatment options: What are alternatives? What non-surgical options exist?
            - Patient care: What services are available? What follow-up is needed?
            - Healthcare settings: Is this outpatient? What facilities provide this?
            - Outcomes: What are success rates? What can patients expect?
            
            Make each question specific and likely to match content in medical procedure documents.
            Vary the question types to maximize semantic coverage for retrieval.
        """
        )
}

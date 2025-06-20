from fastapi import APIRouter
from app.db.base import Database
from app.workflows.generate import generate
from app.workflows.index import index_pdfs

from app.hierarchical_rag.generator import PromptService
from app.core.chunking import ChunkService
from app.core.prompting import PromptProcessor, PromptRunner
from app.core.config import settings
from app.hierarchical_rag.prompts import TEMPLATES
from openai import OpenAI

router = APIRouter()

@router.post("/")
def index_endpoint(
    question_index_name: str,
    chunk_index_name: str,
    embedding_model: str,
    openai_model: str
):
    db = Database(settings.database_url)
    client = OpenAI()
    prompt_service = PromptService(
        processor=PromptProcessor(
            generator=PromptRunner(client=client, model=openai_model),
            templates=TEMPLATES
        )
    )
    chunking_service = ChunkService(method="recursive")

    generate(db=db, prompt_service=prompt_service, chunking_service=chunking_service)
    index_pdfs(db=db, question_index_name=question_index_name, chunk_index_name=chunk_index_name, embedding_model=embedding_model)

    return {"status": "success", "message": "Content generated and indexed"}

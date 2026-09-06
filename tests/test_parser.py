import pytest
from src.parser.base import BaseParser

def test_calculate_score_basic():
    parser = BaseParser()
    repo_data = {"stargazers_count": 100}
    # Test keywords in text
    score = parser._calculate_score("this is an agent for llm", repo_data)
    assert score >= 1

def test_determine_category():
    parser = BaseParser()
    # Test RAG category
    cat = parser._determine_category("this is a rag system with vector db")
    from src.storage.models import Category
    assert cat == Category.RAG

def test_determine_category_other():
    parser = BaseParser()
    cat = parser._determine_category("just some random project")
    from src.storage.models import Category
    assert cat == Category.OTHER

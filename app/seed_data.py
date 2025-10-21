from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Term


TERMS: List[dict] = [
    {
        "keyword": "design-pattern",
        "title": "Паттерн проектирования (Design Pattern)",
        "description": (
            "Типовое архитектурное решение, описывающее способ взаимодействия объектов и классов для решения часто встречающихся задач проектирования. "
            "Делятся на порождающие, структурные и поведенческие (GoF)."
        ),
    },
    {
        "keyword": "static-analysis",
        "title": "Статический анализ (Static Analysis)",
        "description": (
            "Метод исследования исходного кода без его выполнения. Используется для выявления структурных признаков (классы, методы, зависимости), "
            "необходимых при детектировании паттернов."
        ),
    },
    {
        "keyword": "ast",
        "title": "Абстрактное синтаксическое дерево (AST — Abstract Syntax Tree)",
        "description": (
            "Иерархическое представление структуры исходного кода. Применяется для формального описания и поиска шаблонов проектирования на уровне синтаксиса."
        ),
    },
    {
        "keyword": "graph-based-analysis",
        "title": "Графовый анализ (Graph-based Analysis)",
        "description": (
            "Метод представления программ в виде графов зависимостей (class graphs, call graphs), где узлы — сущности, а рёбра — их отношения. "
            "Позволяет искать подграфы, соответствующие структурам паттернов."
        ),
    },
    {
        "keyword": "code-embeddings",
        "title": "Эмбеддинги кода (Code Embeddings)",
        "description": (
            "Векторные представления программного кода, получаемые с помощью языковых моделей (CodeLlama, DeepSeekCoder, CodeBERT). "
            "Используются для обучения классификаторов распознавания паттернов."
        ),
    },
    {
        "keyword": "gnn",
        "title": "Графовые нейронные сети (GNN — Graph Neural Networks)",
        "description": (
            "Архитектуры машинного обучения, обрабатывающие данные в виде графов. Позволяют учитывать контекстные связи между объектами и "
            "повышают точность идентификации шаблонов проектирования."
        ),
    },
    {
        "keyword": "pattern-framework",
        "title": "Фреймворк распознавания паттернов (Pattern Recognition Framework)",
        "description": (
            "Программная система, объединяющая методы анализа кода, построения признаков и классификации. Предназначена для автоматического выявления "
            "архитектурных шаблонов в программных проектах."
        ),
    },
    {
        "keyword": "ml-methods",
        "title": "Методы машинного обучения (Machine Learning Methods)",
        "description": (
            "Класс алгоритмов, используемых для классификации и анализа признаков кода: SVM, Random Forest, MLP, Gradient Boosting. "
            "Применяются для обучения моделей, способных отличать различные паттерны."
        ),
    },
    {
        "keyword": "tsne",
        "title": "t-SNE визуализация (t-distributed Stochastic Neighbor Embedding)",
        "description": (
            "Метод понижения размерности, применяемый для анализа и визуализации многомерных эмбеддингов. "
            "Помогает выявлять скрытые структуры и кластеры, соответствующие различным паттернам."
        ),
    },
    {
        "keyword": "hybrid-approaches",
        "title": "Гибридные подходы к распознаванию (Hybrid Detection Approaches)",
        "description": (
            "Комбинация правил, статического анализа и машинного обучения. Используется для повышения устойчивости алгоритмов к вариативности "
            "реализаций паттернов и различиям в языках программирования."
        ),
    },
]


async def seed_terms(session: AsyncSession) -> None:
    result = await session.execute(select(Term.keyword))
    existing = {k for (k,) in result.all()}
    for term in TERMS:
        if term["keyword"] not in existing:
            session.add(Term(**term))
    await session.flush()

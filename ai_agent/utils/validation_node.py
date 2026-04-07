from langchain_core.prompts import ChatPromptTemplate
from ai_agent.utils.state import AgentState
from ai_agent.utils.retriever_node import build_retriever
from ai_agent.utils.llm_config import llm  # could be GPT4All / LlamaCpp for free

def validate_document(state: AgentState) -> dict:
    """
    Validate latest input message against RAG retrieved sample docs.
    """

    user_input = state["messages"][-1].content

    retriever = build_retriever()

    # Use invoke instead of get_relevant_documents
    docs = retriever.invoke(user_input)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_template("""
You are a strict document validator.

Validate the input ONLY using reference context.

Reference Context:
{context}

Input:
{user_input}

Rules:
- Return VALID if input matches reference
- Return INVALID if mismatch found
- Give short reason

Output:
Status:
Reason:
""")

    chain = prompt | llm

    result = chain.invoke({
        "context": context,
        "user_input": user_input
    })

    return {
        "messages": state["messages"],  # keep conversation
        "validation_result": result.content,
        "current_step": "validated"
    }
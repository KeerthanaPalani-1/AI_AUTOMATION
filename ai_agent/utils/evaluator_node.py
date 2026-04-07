from langchain_classic.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import LLMChain
from ai_agent.utils.state import AgentState
from ai_agent.utils.retriever_node import build_retriever
from ai_agent.utils.llm_config import llm

def evaluate_fix_node(state: AgentState) -> dict:
    corrected_input = state["messages"][-1].content

    retriever = build_retriever()
    docs = retriever.invoke(corrected_input)

    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No reference docs available."

    prompt_template = ChatPromptTemplate.from_template("""
You are a strict evaluator.

Corrected document:
{corrected_input}

Reference context:
{context}

Task:
- Check if the corrected document fully conforms to the reference.
- Return VALID if it matches reference.
- Return INVALID if inconsistencies remain.
- Explain briefly why.

Output format:
Status: VALID or INVALID
Reason: short explanation
""")

    chain = prompt_template | llm

    result = chain.invoke({
        "corrected_input": corrected_input,
        "context": context
    })

    result_text = result.content if hasattr(result, "content") else str(result)

    human_required = (
        "INVALID" in result_text.upper()
        or "no reference docs" in context.lower()
    )

    return {
        "evaluation_status": result_text,
        "human_verification_required": human_required,
        "current_step": "awaiting_human_verification" if human_required else "evaluation_complete"
    }

def human_verification_node(state: AgentState) -> dict:
    evaluation = state["evaluation_status"]
    print("\nLLM Evaluation Result:")
    print(evaluation)

    user_input = input("Approve document? (yes / no): ").strip().lower()

    return {
        "human_approved": user_input == "yes",
        "current_step": "human_approved" if user_input == "yes" else "human_rejected"
    }
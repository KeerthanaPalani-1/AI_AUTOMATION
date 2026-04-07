from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import LLMChain
from langchain.messages import HumanMessage
from ai_agent.utils.state import AgentState
from ai_agent.utils.retriever_node import build_retriever
from ai_agent.utils.llm_config import llm

def fix_document(state: AgentState) -> dict:
    retry_count = state.get("retry_count", 0) + 1
    user_input = state["messages"][-1].content
    validation = state.get("validation_result", "")

    if "INVALID" not in validation.upper():
        return {
            "messages": [HumanMessage(content=user_input)],
            "current_step": "no_fix_needed"
        }

    retriever = build_retriever()

    docs = retriever.invoke(user_input)
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No reference context found."

    prompt = ChatPromptTemplate.from_template("""
You are a strict document fixer.

Input document:
{user_input}

Reference context:
{context}

Task:
- Correct the input so that it fully conforms to the reference context.

Output format:
Return only the corrected document text.
""")

    #chain = LLMChain(prompt=prompt, llm=llm)
    chain = prompt | llm

    corrected = chain.invoke({
        "user_input": user_input,
        "context": context
    })

    fixed_text = corrected.content if hasattr(corrected, "content") else str(corrected)

    return {
        "messages": [HumanMessage(content=fixed_text)],
        "retry_count": retry_count,
        "current_step": "fixed"
    }



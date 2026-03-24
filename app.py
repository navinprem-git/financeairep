import os
import streamlit as st
from typing import List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# --- 1. CONFIGURATION & STATE ---
# Reflects the "AI Gateway" pattern by centralizing configuration
AZURE_SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = "fin-docs-index"

class GraphState(TypedDict):
    """Represents the state of our auditor agent."""
    question: str
    generation: str
    documents: List[str]
    relevance: str

# --- 2. THE ARCHITECTURAL NODES ---

def retrieve(state: GraphState):
    """
    Node: Retrieves documents from Azure AI Search.
    Mirroring the 'Credits DDS' retrieval pattern.
    """
    client = SearchClient(AZURE_SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(AZURE_SEARCH_KEY))
    results = client.search(search_text=state["question"], top=3)
    docs = [res["content"] for res in results]
    return {"documents": docs, "question": state["question"]}

def grade_documents(state: GraphState):
    """
    Node: The 'Four-Eyes' Relevance Check.
    Determines if the retrieved data is sufficient to answer the credit query.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # Simple binary grader logic
    prompt = f"Is this document relevant to the question: {state['question']}? Context: {state['documents']}. Respond with 'yes' or 'no'."
    response = llm.invoke(prompt)
    score = "yes" if "yes" in response.content.lower() else "no"
    return {"relevance": score}

def generate(state: GraphState):
    """
    Node: The Final Auditor Narrative.
    Generates the final 6-step credit proposal logic.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = f"As a Senior Credit Risk Officer, answer the question: {state['question']} using ONLY this context: {state['documents']}"
    response = llm.invoke(prompt)
    return {"generation": response.content}

# --- 3. BUILDING THE GRAPH (The Agentic Logic) ---

workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)

# Define Flow
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")

# Senior Pattern: Conditional Branching
workflow.add_conditional_edges(
    "grade_documents",
    lambda x: x["relevance"],
    {
        "yes": "generate",
        "no": END  # In a real app, this would route to 'Web Search'
    }
)

workflow.add_edge("generate", END)
app = workflow.compile()

# --- 4. STREAMLIT UI ---

st.set_page_config(page_title="Agentic Financial Auditor", page_icon="🏦")
st.title("🏦 Agentic Financial Auditor")
st.caption("Enterprise-Grade C-RAG for Credit Risk Analysis")

query = st.text_input("Enter a financial query (e.g., 'What is the debt-to-equity ratio of MSFT?')")

if st.button("Analyze"):
    with st.spinner("Agent thinking..."):
        # Run the Graph
        inputs = {"question": query}
        result = app.invoke(inputs)
        
        if result.get("generation"):
            st.markdown("### 📋 Credit Analysis Report")
            st.write(result["generation"])
        else:
            st.error("The system could not find enough relevant data to provide a safe answer.")

    # Show Traceability (The 'Senior Architect' Flex)
    with st.expander("🔍 View Audit Trace (Metadata & Sources)"):
        st.json(result["documents"])

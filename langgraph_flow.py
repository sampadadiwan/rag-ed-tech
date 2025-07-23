from embedder import get_gemini_embedder
from vectorstore import get_vectorstore, retrieve_documents
from websearch_tool import get_web_search_tool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI

# State definition
from typing import TypedDict, List, Optional
class GraphState(TypedDict):
    question: str
    file_id: str
    docs: Optional[List[str]]
    answer: Optional[str]

# Nodes
def retrieve_docs(state: GraphState) -> GraphState:
    embedder = get_gemini_embedder()
    vectordb = get_vectorstore(embedder,state["file_id"])
    docs = retrieve_documents(state["question"], vectordb)
    # ✅ Check if any documents were retrieved
    print("Number of documents retrieved:", len(docs))

    # Optional: Show the first few documents
    if docs:
        print("First document content snippet:")
        print(docs[0].page_content[:300])  # show first 300 chars
    else:
        print("No documents found for the question.")
    
    return {**state, "docs": docs}

def is_enough_docs(state: GraphState) -> bool:
    print("Checking if enough documents were retrieved...")
    print("Returning:", bool(state["docs"]))
    return bool(state["docs"])

def generate_answer_from_docs(state: GraphState) -> GraphState:
    llm = ChatOpenAI(model="gpt-4", temperature=0.0)
    context = "\n\n".join([doc.page_content for doc in state["docs"]])
    print("Context for LLM:", context[:300])  # show first 300 chars of context
    prompt =  f"""
    You are an expert in answering questions based on provided context from a book. Use the context below to answer the question.
    {context}
    Question: {state['question']}
    """
    
  
    answer = llm.invoke(prompt)
    print("Generated answer:", answer.content[:300])  # show first 300 chars of answer
    if not answer.content:
        print("Warning: Generated answer is empty!")
    return {**state, "answer": answer.content}

def generate_answer_from_web(state: GraphState) -> GraphState:
    tool = get_web_search_tool()
    results = tool.invoke({"query": state["question"]})
    pages = "\n".join([r["content"] for r in results])
    llm = ChatOpenAI()
    prompt = """Answer this question using info from the web:

            {pages}

            Question: {state['question']}"""
    answer = llm.invoke(prompt)
    return {**state, "answer": answer.content}

# Build LangGraph
def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve_docs)
    workflow.add_node("answer_from_doc", generate_answer_from_docs)
    workflow.add_node("answer_from_web", generate_answer_from_web)

    workflow.set_entry_point("retrieve")
    workflow.add_conditional_edges("retrieve", is_enough_docs, {
        True: "answer_from_doc",
        False: "answer_from_web"
    })
    workflow.add_edge("answer_from_doc", END)
    workflow.add_edge("answer_from_web", END)

    return workflow.compile()

graph = build_graph()

def run_qa(query: str, file_id: str):
    print("Prompt question going to RAG chain:", query)
    print("File ID for RAG chain:", file_id)
    inputs = {"question": query, "file_id": file_id}
    result = graph.invoke(inputs)
    return result["answer"]

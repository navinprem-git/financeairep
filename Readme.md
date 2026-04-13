# AI Lending Assistant: End-to-End Financial Auditor

### 🚀 Overview
A production-grade architectural blueprint for transforming manual-intensive lending audits into an AI-assisted workflow. 

### 🏗️ Key Architectural Features
- **Agentic RAG:** Built with LangGraph to implement a "Corrective RAG" pattern.
- **Document Shredding:** Uses Azure AI Search Index Projections to handle 100+ page 10-K PDFs without hitting LLM context limits.
- **Automated Grading:** A dedicated Grader node evaluates document relevance before generation to prevent financial hallucinations.

- graph TD
    %% User and UI Layer
    User([User Query]) --> UI[Streamlit UI]
    UI --> LG_State{LangGraph <br/>State Manager}

    %% Azure Infrastructure Layer
    subgraph Azure_Data_Pipeline [Data Ingestion & Shredding]
        Blob[(Azure Blob Storage <br/>'finance-pdfs')] 
        Indexer[Azure Search Indexer]
        Skillset[AI Skillset <br/>'SplitSkill / Shredder']
        Index[(Search Index <br/>'Shredded Chunks')]
        
        Blob --> Indexer
        Indexer --> Skillset
        Skillset --> Index
    end

    %% Agentic Workflow Layer
    subgraph LangGraph_Workflow [Agentic RAG Logic]
        LG_State --> Retrieve[Node: Retrieve Chunks]
        Retrieve <--> Index
        
        Retrieve --> Grade[Node: Document Grader]
        
        Grade --> Choice{Data Relevant?}
        
        Choice -- "Yes" --> Generate[Node: Generate Answer]
        Choice -- "No" --> NotFound[Node: Data Not Found]
    end

    %% Final Output
    Generate --> UI
    NotFound -- "I've audited the 10-K and..." --> UI

    %% Styling
    style LG_State fill:#f9f,stroke:#333,stroke-width:2px
    style Azure_Data_Pipeline fill:#f0f7ff,stroke:#0078d4,stroke-width:2px
    style Choice fill:#fff4dd,stroke:#d4a017,stroke-width:2px

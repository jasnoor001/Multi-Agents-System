# app.py

import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# Page configuration
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Background */

.stApp{
    background: linear-gradient(
        135deg,
        #0f172a,
        #111827,
        #1e293b
    );
    color:white;
}

/* Hide Streamlit menu */

#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

/* Title */

.title{
text-align:center;
font-size:48px;
font-weight:700;
color:white;
margin-bottom:0px;
}

.subtitle{
text-align:center;
color:#94a3b8;
font-size:18px;
margin-bottom:35px;
}

/* Cards */

.card{

background:rgba(255,255,255,.05);

backdrop-filter:blur(12px);

padding:25px;

border-radius:20px;

border:1px solid rgba(255,255,255,.08);

box-shadow:0px 10px 30px rgba(0,0,0,.4);

margin-bottom:20px;

}

/* Agent cards */

.agent{

padding:18px;

border-radius:15px;

margin-bottom:15px;

background:#1e293b;

border-left:6px solid #38bdf8;

font-size:18px;

}

/* Success */

.success{

border-left:6px solid #10b981;

}

/* Running */

.running{

border-left:6px solid orange;

}

/* Waiting */

.wait{

border-left:6px solid gray;

}

/* Buttons */

.stButton>button{

width:100%;

background:linear-gradient(90deg,#2563eb,#7c3aed);

color:white;

border:none;

padding:15px;

font-size:18px;

font-weight:600;

border-radius:15px;

transition:0.3s;

}

.stButton>button:hover{

transform:scale(1.02);

box-shadow:0px 10px 25px rgba(37,99,235,.5);

}

/* Text Input */

.stTextInput input{

background:#1e293b;

color:white;

border-radius:12px;

border:1px solid #334155;

padding:12px;

}

/* Progress */

.stProgress > div > div > div{

background:linear-gradient(90deg,#2563eb,#7c3aed);

}

/* Tabs */

.stTabs [data-baseweb="tab"]{

background:#1e293b;

border-radius:10px;

padding:10px 20px;

}

</style>

""",unsafe_allow_html=True)

# Title and description
st.title("🔍 AI Research Agent")
st.markdown("A multi-agent system that searches, scrapes, writes, and critiques research reports.")

st.divider()

# Input section
topic = st.text_input(
    "Enter your research topic:",
    placeholder="e.g., Latest developments in quantum computing"
)

# Initialize session state
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 0


def run_research_pipeline(topic: str) -> dict:
    """Run the full research pipeline with UI updates."""
    
    state = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create expandable sections for each step
    search_expander = st.expander("📡 Step 1: Search Agent", expanded=True)
    reader_expander = st.expander("📖 Step 2: Reader Agent", expanded=False)
    writer_expander = st.expander("✍️ Step 3: Writer Agent", expanded=False)
    critic_expander = st.expander("🎯 Step 4: Critic Agent", expanded=False)
    
    # Step 1 - Search Agent
    with search_expander:
        status_text.text("🔍 Search Agent is finding information...")
        st.info("Searching for recent, reliable information...")
        
        with st.spinner("Searching..."):
            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"find recent, reliable and detailed information about: {topic}")]
            })
            state["search_result"] = search_result["messages"][-1].content
        
        st.success("Search completed!")
        st.text_area("Search Results:", state["search_result"], height=200, key="search_results")
    
    progress_bar.progress(25)
    
    # Step 2 - Reader Agent
    with reader_expander:
        status_text.text("📖 Reader Agent is scraping content...")
        st.info("Scraping top resources for deeper content...")
        
        with st.spinner("Scraping web pages..."):
            reader_agent = build_reader_agent()
            reader_result = reader_agent.invoke({
                "messages": [("user",
                    f"based on the following search results about '{topic}',"
                    f"Pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search results:\n{state['search_result'][:800]}"
                )]
            })
            state["scraped_content"] = reader_result["messages"][-1].content
        
        st.success("Scraping completed!")
        st.text_area("Scraped Content:", state["scraped_content"], height=200, key="scraped_content")
    
    progress_bar.progress(50)
    
    # Step 3 - Writer Chain
    with writer_expander:
        status_text.text("✍️ Writer is drafting the report...")
        st.info("Generating comprehensive research report...")
        
        with st.spinner("Writing report..."):
            research_combined = (
                f"SEARCH RESULTS:\n{state['search_result']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
            )
            
            state["report"] = writer_chain.invoke({
                "topic": topic,
                "research": research_combined
            })
        
        st.success("Report drafted!")
        st.markdown("### Draft Report")
        st.markdown(state["report"])
    
    progress_bar.progress(75)
    
    # Step 4 - Critic Chain
    with critic_expander:
        status_text.text("🎯 Critic is reviewing the report...")
        st.info("Analyzing report quality and providing feedback...")
        
        with st.spinner("Reviewing..."):
            state["feedback"] = critic_chain.invoke({
                "report": state["report"]
            })
        
        st.success("Review completed!")
        st.markdown("### Critic's Feedback")
        st.markdown(state["feedback"])
    
    progress_bar.progress(100)
    status_text.text("✅ Pipeline completed successfully!")
    
    return state


# Run button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    run_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

# Execute pipeline
if run_button:
    if not topic.strip():
        st.error("Please enter a research topic.")
    else:
        st.divider()
        st.header(f"Research: {topic}")
        
        try:
            st.session_state.pipeline_state = run_research_pipeline(topic)
            
            # Final summary
            st.divider()
            st.header("📋 Summary")
            
            tab1, tab2, tab3 = st.tabs(["📄 Final Report", "💬 Feedback", "🔗 Raw Data"])
            
            with tab1:
                st.markdown(st.session_state.pipeline_state["report"])
                st.download_button(
                    label="📥 Download Report",
                    data=st.session_state.pipeline_state["report"],
                    file_name=f"research_report_{topic.replace(' ', '_')[:30]}.md",
                    mime="text/markdown"
                )
            
            with tab2:
                st.markdown(st.session_state.pipeline_state["feedback"])
            
            with tab3:
                st.json({
                    "topic": topic,
                    "search_result_length": len(st.session_state.pipeline_state["search_result"]),
                    "scraped_content_length": len(st.session_state.pipeline_state["scraped_content"]),
                    "report_length": len(st.session_state.pipeline_state["report"]),
                    "feedback_length": len(st.session_state.pipeline_state["feedback"])
                })
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This multi-agent research system uses:
    
    1. **Search Agent** - Finds relevant information online
    2. **Reader Agent** - Scrapes and extracts detailed content
    3. **Writer Agent** - Composes a comprehensive report
    4. **Critic Agent** - Reviews and provides feedback
    """)
    
    st.divider()
    
    st.header("💡 Tips")
    st.markdown("""
    - Be specific with your research topic
    - Complex topics may take longer to process
    - Check the feedback tab for improvement suggestions
    """)
    
    st.divider()
    
    st.header("🛠️ System Status")
    st.success("All agents ready")

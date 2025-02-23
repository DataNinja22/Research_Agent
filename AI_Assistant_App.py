import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# UI Configuration
st.set_page_config(page_title="AI Research Assistant", page_icon="📚", layout="centered")

# Sidebar Configuration
with st.sidebar:
    st.header("Assistant Overview")
    st.info("This AI assistant leverages the power of CrewAI and OpenAI GPT models to conduct intelligent research. It employs autonomous agents, including a Research Specialist for data gathering and a Technical Writer for structured content generation. These agents collaborate to synthesize insights from real-time sources, academic research, and news articles—delivering concise, well-structured reports in multiple formats.")

    # Input for API Keys
    openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")
    serper_api_key = st.text_input("🔑 Serper API Key", type="password")

    # Model Selection
    selected_model = st.selectbox("🤖 Choose Model", ["gpt-3.5-turbo", "gpt-4o-mini", "o3-mini"])

    # Research Preferences
    include_news = st.checkbox("Include recent news", value=True)  #Will be checked by default
    include_academic = st.checkbox("Include academic sources", value=True) #Will be checked by default
    output_format = st.selectbox("Output format", ["Markdown", "HTML", "Plain Text"])


# Function to initialize LLM and search tool
@st.cache_resource
def initialize_tools(api_key, search_api_key, model_name):
    llm = ChatOpenAI(model=model_name, temperature=0.3, openai_api_key=api_key)
    search_tool = SerperDevTool(api_key=search_api_key)
    return llm, search_tool

# Function to initialize Agents
def initialize_agents(llm, search_tool):
    research_agent = Agent(
        role="Research Specialist",
        goal="Conduct fast, accurate research on the given topic",
        backstory="Expert in information gathering and analysis",
        verbose=True,
        memory=False,
        tools=[search_tool],
        llm=llm
    )
    
    writer_agent = Agent(
        role="Technical Research Writer",
        goal="Create concise, structured reports",
        backstory="Specialist in clear, precise technical research paper writing",
        verbose=True,
        memory=False,
        tools=[search_tool],
        llm=llm
    )
    return research_agent, writer_agent

# Function to run research pipeline and stream output
def run_research_pipeline(topic, include_news, include_academic, output_format):
    try:
        llm, search_tool = initialize_tools(openai_api_key,serper_api_key,selected_model)
        research_agent, writer_agent = initialize_agents(llm, search_tool)

        # Modify research task based on settings
        research_description = f"Find key information about: {topic}"
        if include_news:
            research_description += " Include the latest news articles."
        if include_academic:
            research_description += " Also include research papers and academic sources."

        research_task = Task(
            description=research_description,
            agent=research_agent,
            expected_output="Detailed Bullet points of key facts, recent developments, and academic references."
            if include_academic 
            else "Bullet points of key facts and recent developments.",
            async_execution=True  # If you want totally sequential then Update to False
        )

        writing_task = Task(
            description=f"Create structured report on: {topic} in {output_format} format.",
            agent=writer_agent,
            expected_output=f" A {output_format} document with:\n- Introduction\n- Key Findings\n- Recent Developments\n- Future Outlook\n- References",
            context=[research_task]
        )

        crew = Crew(agents=[research_agent, writer_agent], tasks=[research_task, writing_task])
        
        result = crew.kickoff(inputs={'topic': topic})
        
        return result



    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


# Custom CSS for better UI
st.markdown("""
    <style>
    .report-output {
    padding: 20px;
    border-radius: 10px;
    background: #2c3e50; /* Darker blue-gray */
    border: 1px solid #34495e; /* Slightly darker border */
    color: white; /* Ensures text is readable */
}
    .powered-by {
        text-align: center;
        color: #666;
        font-size: 0.9em;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Main App UI
st.header("📚 AI Research Assistant", divider="rainbow")

col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Enter the Research Topic : ", placeholder="e.g., Quantum Computing Advances 2024")

st.caption("Powered by OpenAI and CrewAI")

if col2.button("Start Research", use_container_width=True):
    
        if not topic:
            st.warning("Please enter the research topic")
        else:
            with st.spinner("🚀 Launching research agents and generating the report..."):
                result = run_research_pipeline(topic, include_news, include_academic, output_format)
                    
                if result:
                    st.markdown("## Research Report")
                    st.markdown(f'<div class="report-output">{result}</div>', unsafe_allow_html=True)
                
                st.divider()
                st.markdown('<p class="powered-by">Powered by OpenAI and CrewAI</p>', unsafe_allow_html=True)

        st.success("✅ Research complete!")



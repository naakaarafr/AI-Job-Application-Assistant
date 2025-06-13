from crewai import Agent
from tools import scrape_tool, search_tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator to retry function calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    # Check if it's a 503 or rate limit error
                    error_str = str(e).lower()
                    if "503" in error_str or "overloaded" in error_str or "rate limit" in error_str:
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        print(f"Model overloaded, retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        # For other errors, raise immediately
                        raise e
            return None
        return wrapper
    return decorator

# Initialize the Gemini LLM with enhanced error handling
@retry_with_backoff(max_retries=3, base_delay=2, max_delay=30)
def get_gemini_llm():
    """Initialize and return Google Gemini LLM with fallback options"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    
    # Try different models in order of preference
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    for model in models_to_try:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=0.7,
                convert_system_message_to_human=True,
                # Add request timeout and retry settings
                request_timeout=60,
                max_retries=2,
                # Add rate limiting parameters
                max_tokens_per_minute=50000,
                max_requests_per_minute=50
            )
            
            # Test the model with a simple call
            test_response = llm.invoke("Hello")
            print(f"✅ Successfully initialized {model}")
            return llm
            
        except Exception as e:
            print(f"⚠️ Failed to initialize {model}: {str(e)}")
            if model == models_to_try[-1]:  # Last model in the list
                raise e
            continue
    
    raise Exception("All Gemini models failed to initialize")

def get_gemini_llm_with_config(temperature=0.7, max_tokens=None):
    """Get Gemini LLM with custom configuration"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    
    config = {
        "model": "gemini-2.0-flash",
        "google_api_key": api_key,
        "temperature": temperature,
        "convert_system_message_to_human": True,
        "request_timeout": 120,  # Longer timeout
        "max_retries": 3
    }
    
    if max_tokens:
        config["max_output_tokens"] = max_tokens
    
    return ChatGoogleGenerativeAI(**config)

# Agent 1: Researcher
def create_researcher():
    return Agent(
        role="Tech Job Researcher",
        goal="Make sure to do amazing analysis on "
             "job posting to help job applicants",
        tools=[scrape_tool, search_tool],
        verbose=True,
        backstory=(
            "As a Job Researcher, your prowess in "
            "navigating and extracting critical "
            "information from job postings is unmatched."
            "Your skills help pinpoint the necessary "
            "qualifications and skills sought "
            "by employers, forming the foundation for "
            "effective application tailoring."
        ),
        llm=get_gemini_llm(),
        max_iter=3,  # Limit iterations to prevent long runs
        max_execution_time=300,  # 5 minute timeout
    )

# Agent 2: Profiler
def create_profiler(read_resume, semantic_search_resume):
    return Agent(
        role="Personal Profiler for Engineers",
        goal="Do incredible research on job applicants "
             "to help them stand out in the job market",
        tools=[scrape_tool, search_tool, read_resume, semantic_search_resume],
        verbose=True,
        backstory=(
            "Equipped with analytical prowess, you dissect "
            "and synthesize information "
            "from diverse sources to craft comprehensive "
            "personal and professional profiles, laying the "
            "groundwork for personalized resume enhancements."
        ),
        llm=get_gemini_llm(),
        max_iter=3,
        max_execution_time=300,
    )

# Agent 3: Resume Strategist
def create_resume_strategist(read_resume, semantic_search_resume):
    return Agent(
        role="Resume Strategist for Engineers",
        goal="Find all the best ways to make a "
             "resume stand out in the job market.",
        tools=[scrape_tool, search_tool, read_resume, semantic_search_resume],
        verbose=True,
        backstory=(
            "With a strategic mind and an eye for detail, you "
            "excel at refining resumes to highlight the most "
            "relevant skills and experiences, ensuring they "
            "resonate perfectly with the job's requirements."
        ),
        llm=get_gemini_llm(),
        max_iter=3,
        max_execution_time=300,
    )

# Agent 4: Interview Preparer
def create_interview_preparer(read_resume, semantic_search_resume):
    return Agent(
        role="Engineering Interview Preparer",
        goal="Create interview questions and talking points "
             "based on the resume and job requirements",
        tools=[scrape_tool, search_tool, read_resume, semantic_search_resume],
        verbose=True,
        backstory=(
            "Your role is crucial in anticipating the dynamics of "
            "interviews. With your ability to formulate key questions "
            "and talking points, you prepare candidates for success, "
            "ensuring they can confidently address all aspects of the "
            "job they are applying for."
        ),
        llm=get_gemini_llm(),
        max_iter=3,
        max_execution_time=300,
    )

# Alternative function to create agents with different models for load balancing
def create_agents_with_load_balancing(read_resume, semantic_search_resume):
    """Create agents with different models to distribute load"""
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    agents = []
    for i, (agent_name, agent_func) in enumerate([
        ("researcher", create_researcher),
        ("profiler", lambda: create_profiler(read_resume, semantic_search_resume)),
        ("resume_strategist", lambda: create_resume_strategist(read_resume, semantic_search_resume)),
        ("interview_preparer", lambda: create_interview_preparer(read_resume, semantic_search_resume))
    ]):
        # Use different models for different agents
        model = models[i % len(models)]
        try:
            if agent_name == "researcher":
                agent = create_researcher()
            else:
                agent = agent_func()
            agents.append(agent)
        except Exception as e:
            print(f"Failed to create {agent_name} with {model}: {e}")
            # Fallback to default model
            agent = agent_func()
            agents.append(agent)
    
    return agents
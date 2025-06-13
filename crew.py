from crewai import Crew
from agents import create_researcher, create_profiler, create_resume_strategist, create_interview_preparer
from tasks import create_tasks
from tools import get_resume_tools_advanced

def create_job_application_crew(job_posting_url, github_url, personal_writeup, resume_path):
    """Create the job application crew with dynamic tasks and agents"""
    
    # Get resume tools - now supports PDF, MD, and TXT files
    try:
        read_resume, semantic_search_resume = get_resume_tools_advanced(resume_path)
        print(f"✅ Successfully initialized resume tools for: {resume_path}")
    except Exception as e:
        print(f"❌ Error initializing resume tools: {e}")
        raise e
    
    # Create agents with resume tools
    researcher = create_researcher()
    profiler = create_profiler(read_resume, semantic_search_resume)
    resume_strategist = create_resume_strategist(read_resume, semantic_search_resume)
    interview_preparer = create_interview_preparer(read_resume, semantic_search_resume)
    
    # Create tasks with the provided parameters and agents
    research_task, profile_task, resume_strategy_task, interview_preparation_task = create_tasks(
        job_posting_url, github_url, personal_writeup, researcher, profiler, resume_strategist, interview_preparer
    )
    
    # Create and return the crew
    job_application_crew = Crew(
        agents=[researcher, profiler, resume_strategist, interview_preparer],
        tasks=[research_task, profile_task, resume_strategy_task, interview_preparation_task],
        verbose=True
    )
    
    return job_application_crew
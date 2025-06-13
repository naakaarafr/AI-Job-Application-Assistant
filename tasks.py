from crewai import Task

def create_tasks(job_posting_url, github_url, personal_writeup, researcher, profiler, resume_strategist, interview_preparer):
    # Task for Researcher Agent: Extract Job Requirements
    research_task = Task(
        description=(
            f"Analyze the job posting URL provided ({job_posting_url}) "
            "to extract key skills, experiences, and qualifications "
            "required. Use the tools to gather content and identify "
            "and categorize the requirements."
        ),
        expected_output=(
            "A structured list of job requirements, including necessary "
            "skills, qualifications, and experiences."
        ),
        agent=researcher
        # Removed async_execution=True to avoid event loop issues in Streamlit
    )

    # Task for Profiler Agent: Compile Comprehensive Profile
    profile_task = Task(
        description=(
            f"Compile a detailed personal and professional profile "
            f"using the GitHub ({github_url}) URLs, and personal write-up "
            f"({personal_writeup}). Utilize tools to extract and "
            "synthesize information from these sources."
        ),
        expected_output=(
            "A comprehensive profile document that includes skills, "
            "project experiences, contributions, interests, and "
            "communication style."
        ),
        agent=profiler
        # Removed async_execution=True to avoid event loop issues in Streamlit
    )

    # Task for Resume Strategist Agent: Align Resume with Job Requirements
    resume_strategy_task = Task(
        description=(
            "Using the profile and job requirements obtained from "
            "previous tasks, tailor the resume to highlight the most "
            "relevant areas. Employ tools to adjust and enhance the "
            "resume content. Make sure this is the best resume even but "
            "don't make up any information. Update every section, "
            "including the initial summary, work experience, skills, "
            "and education. All to better reflect the candidates "
            "abilities and how it matches the job posting."
        ),
        expected_output=(
            "An updated resume that effectively highlights the candidate's "
            "qualifications and experiences relevant to the job."
        ),
        output_file="tailored_resume.md",
        context=[research_task, profile_task],
        agent=resume_strategist
    )

    # Task for Interview Preparer Agent: Develop Interview Materials
    interview_preparation_task = Task(
        description=(
            "Create a set of potential interview questions and talking "
            "points based on the tailored resume and job requirements. "
            "Utilize tools to generate relevant questions and discussion "
            "points. Make sure to use these questions and talking points to "
            "help the candidate highlight the main points of the resume "
            "and how it matches the job posting."
        ),
        expected_output=(
            "A document containing key questions and talking points "
            "that the candidate should prepare for the initial interview."
        ),
        output_file="interview_materials.md",
        context=[research_task, profile_task, resume_strategy_task],
        agent=interview_preparer
    )

    return research_task, profile_task, resume_strategy_task, interview_preparation_task
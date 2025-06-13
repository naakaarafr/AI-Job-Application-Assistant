import streamlit as st
import os
import tempfile
import asyncio
import nest_asyncio
import time
import random
from crew import create_job_application_crew
from tools import get_resume_tools_advanced
import PyPDF2

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Set up page config
st.set_page_config(
    page_title="AI Job Application Assistant",
    page_icon="💼",
    layout="wide"
)

def run_crew_with_retry(crew, max_retries=3):
    """Run crew with retry logic for handling overloaded models"""
    for attempt in range(max_retries):
        try:
            return crew.kickoff()
        except Exception as e:
            error_str = str(e).lower()
            if ("503" in error_str or "overloaded" in error_str or 
                "rate limit" in error_str or "quota" in error_str):
                
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    st.warning(f"⏳ Model is overloaded. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    st.error("❌ All retry attempts failed. Please try again in a few minutes.")
                    raise e
            else:
                # For other errors, don't retry
                raise e
    return None

def run_crew_sync(crew):
    """Run crew synchronously, handling event loop issues"""
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to use nest_asyncio
            return run_crew_with_retry(crew)
        else:
            # If loop exists but not running, run it
            return loop.run_until_complete(asyncio.create_task(run_crew_with_retry(crew)))
    except RuntimeError:
        # No event loop exists, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return run_crew_with_retry(crew)
        finally:
            # Don't close the loop as it might be needed elsewhere
            pass

# Title and description
st.title("🤖 AI Job Application Assistant")
st.markdown("Upload your resume and let our AI agents help you tailor it for your dream job!")

# Add status indicator for API health
with st.sidebar:
    st.header("🔧 System Status")
    
    # Check API keys
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if google_key:
        st.success("✅ Google API Key configured")
    else:
        st.error("❌ Google API Key missing")
    
    if serper_key:
        st.success("✅ Serper API Key configured")
    else:
        st.error("❌ Serper API Key missing")
    
    # Add tips for handling overloaded models
    st.markdown("### 💡 Tips for Success")
    st.markdown("""
    - **Model Overloaded?** The app will automatically retry with backoff
    - **Peak Hours:** Try using the app during off-peak hours (early morning/late evening)
    - **Large Files:** Smaller resume files process faster
    - **Internet:** Ensure stable internet connection
    """)
    
    # Add current time
    st.markdown(f"**Current Time:** {time.strftime('%H:%M:%S')}")

# Main interface
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['md', 'txt', 'pdf'],
        help="Upload your resume in PDF (.pdf), Markdown (.md) or text (.txt) format"
    )
    
    resume_path = None
    if uploaded_file is not None:
        # Get file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Show file size
        file_size = len(uploaded_file.getvalue())
        st.info(f"📊 File size: {file_size / 1024:.1f} KB")
        
        # Save uploaded file temporarily
        if file_extension == '.pdf':
            # For PDF files, save as binary
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                resume_path = tmp_file.name
        else:
            # For text/markdown files, save as text
            with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(uploaded_file.getvalue().decode('utf-8'))
                resume_path = tmp_file.name
        
        st.success(f"✅ Resume uploaded successfully! ({file_extension.upper()} format)")
        
        # Show file preview for PDF files
        if file_extension == '.pdf':
            try:
                # Extract and show first few lines of PDF
                with open(resume_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if len(pdf_reader.pages) > 0:
                        first_page_text = pdf_reader.pages[0].extract_text()
                        preview_text = first_page_text[:300] + "..." if len(first_page_text) > 300 else first_page_text
                        st.text_area("PDF Preview (First 300 characters):", preview_text, height=100, disabled=True)
                        st.info(f"📊 PDF contains {len(pdf_reader.pages)} page(s)")
            except Exception as e:
                st.warning(f"Could not preview PDF: {str(e)}")
        
        # Test resume tools
        try:
            read_resume, semantic_search_resume = get_resume_tools_advanced(resume_path)
            st.success("✅ Resume tools initialized!")
            
            # Test if we can read content
            try:
                if file_extension == '.pdf':
                    # For PDF files, test the search tool with a query
                    if hasattr(semantic_search_resume, 'run'):
                        test_content = semantic_search_resume.run("skills")
                    else:
                        # Fallback: read the file directly if it's been converted to text
                        test_content = read_resume.run()
                else:
                    # For text/markdown files, just read the content
                    test_content = read_resume.run()
                
                if test_content and len(str(test_content).strip()) > 0:
                    st.success("✅ Resume content successfully extracted!")
                    # Show a small preview of extracted content
                    preview = str(test_content)[:200] + "..." if len(str(test_content)) > 200 else str(test_content)
                    st.text_area("Content Preview:", preview, height=100, disabled=True)
                else:
                    st.warning("⚠️ Resume uploaded but content extraction may be limited")
            except Exception as e:
                st.warning(f"⚠️ Resume uploaded but there might be issues with content extraction: {str(e)}")
                st.info("This might not affect the main processing - the tools may still work correctly during actual processing.")
            
        except Exception as e:
            st.error(f"❌ Error initializing resume tools: {str(e)}")
            st.error("Please try uploading a different file format or check if the file is corrupted.")

with col2:
    st.header("🎯 Job Details")
    job_posting_url = st.text_input(
        "Job Posting URL",
        placeholder="https://example.com/job-posting",
        help="Enter the URL of the job posting you're applying for"
    )
    
    github_url = st.text_input(
        "GitHub Profile URL",
        placeholder="https://github.com/yourusername",
        help="Your GitHub profile URL (optional)"
    )
    
    personal_writeup = st.text_area(
        "Personal Write-up",
        placeholder="Write a brief description about yourself, your goals, and what makes you unique...",
        height=150,
        help="A personal summary that highlights your strengths and career objectives"
    )

# Process button
st.header("🚀 Generate Application Materials")

# Add warning about peak usage
current_hour = time.localtime().tm_hour
if 9 <= current_hour <= 17:  # Business hours
    st.warning("⏰ Peak usage hours detected. Processing may take longer due to high demand. Consider trying during off-peak hours for faster results.")

if st.button("🎯 Tailor My Application", type="primary", use_container_width=True):
    # Validation
    if not uploaded_file or not resume_path:
        st.error("❌ Please upload your resume first!")
    elif not job_posting_url:
        st.error("❌ Please enter a job posting URL!")
    else:
        # Check for required environment variables
        google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        serper_key = os.getenv("SERPER_API_KEY")
        
        missing_vars = []
        if not google_key:
            missing_vars.append("GOOGLE_API_KEY or GEMINI_API_KEY")
        if not serper_key:
            missing_vars.append("SERPER_API_KEY")
        
        if missing_vars:
            st.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            st.info("Please set up your API keys in your environment variables and restart the app.")
        else:
            try:
                with st.spinner("🤖 AI agents are working on your application..."):
                    # Create progress indicators
                    progress_container = st.container()
                    with progress_container:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                    
                    # Add estimated time
                    start_time = time.time()
                    status_text.text("🔍 Creating AI crew... (Estimated time: 2-5 minutes)")
                    progress_bar.progress(5)
                    
                    # Create crew
                    crew = create_job_application_crew(
                        job_posting_url=job_posting_url,
                        github_url=github_url or "Not provided",
                        personal_writeup=personal_writeup or "Not provided",
                        resume_path=resume_path
                    )
                    
                    progress_bar.progress(15)
                    status_text.text("🔍 Analyzing job posting... (This may take a while)")
                    
                    progress_bar.progress(30)
                    status_text.text("👤 Building your profile...")
                    
                    progress_bar.progress(50)
                    status_text.text("📝 Tailoring your resume...")
                    
                    progress_bar.progress(75)
                    status_text.text("🎤 Preparing interview materials...")
                    
                    progress_bar.progress(90)
                    status_text.text("⚡ Finalizing results...")
                    
                    # Run the crew with improved error handling
                    result = run_crew_sync(crew)
                    
                    progress_bar.progress(100)
                    elapsed_time = time.time() - start_time
                    status_text.text(f"✅ Complete! (Processed in {elapsed_time:.1f} seconds)")
                    
                    st.success("🎉 Your application materials have been generated!")
                    
                    # Display results
                    result_col1, result_col2 = st.columns(2)
                    
                    with result_col1:
                        st.header("📄 Tailored Resume")
                        if os.path.exists("tailored_resume.md"):
                            with open("tailored_resume.md", "r", encoding='utf-8') as f:
                                resume_content = f.read()
                            st.markdown(resume_content)
                            st.download_button(
                                "📥 Download Tailored Resume",
                                resume_content,
                                "tailored_resume.md",
                                "text/markdown"
                            )
                        else:
                            st.warning("Resume file not found. The content might be in the result object.")
                            if result:
                                st.text_area("Generated Content:", str(result)[:2000], height=300)
                    
                    with result_col2:
                        st.header("🎤 Interview Preparation")
                        if os.path.exists("interview_materials.md"):
                            with open("interview_materials.md", "r", encoding='utf-8') as f:
                                interview_content = f.read()
                            st.markdown(interview_content)
                            st.download_button(
                                "📥 Download Interview Materials",
                                interview_content,
                                "interview_materials.md",
                                "text/markdown"
                            )
                        else:
                            st.warning("Interview materials file not found. Check the logs for errors.")
                    
                    # Show raw result if files weren't created
                    if not os.path.exists("tailored_resume.md") and not os.path.exists("interview_materials.md"):
                        st.header("📋 Generated Content")
                        st.text_area("Raw Output:", str(result), height=400)
                    
                    # Clean up temporary files
                    try:
                        if resume_path and os.path.exists(resume_path):
                            os.unlink(resume_path)
                        # Clean up any temporary text files created from PDF conversion
                        temp_dir = tempfile.gettempdir()
                        for file in os.listdir(temp_dir):
                            if file.startswith('tmp') and file.endswith('.txt'):
                                try:
                                    os.unlink(os.path.join(temp_dir, file))
                                except:
                                    pass
                    except Exception as cleanup_error:
                        st.warning(f"Note: Some temporary files could not be cleaned up: {cleanup_error}")
                        
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.error(f"Error type: {type(e).__name__}")
                
                # Specific handling for common errors
                error_str = str(e).lower()
                if "503" in error_str or "overloaded" in error_str:
                    st.error("🚨 **Model Overloaded Error**")
                    st.info("""
                    **What to do:**
                    1. ⏰ **Wait 5-10 minutes** and try again
                    2. 🌙 **Try during off-peak hours** (early morning/late evening)
                    3. 🔄 **Refresh the page** and try again
                    4. 📧 If the problem persists, the service may be experiencing high demand
                    """)
                elif "rate limit" in error_str or "quota" in error_str:
                    st.error("🚨 **Rate Limit Exceeded**")
                    st.info("Please wait a few minutes before trying again. The API has usage limits.")
                
                # More detailed error information
                import traceback
                with st.expander("🔍 Detailed Error Information"):
                    st.code(traceback.format_exc())
                
                st.info("💡 **Troubleshooting Tips:**")
                st.markdown("""
                - Check your internet connection
                - Verify your API keys are correct
                - Try with a smaller resume file
                - Wait and try again during off-peak hours
                """)
                
                # Clean up temporary file on error
                if resume_path:
                    try:
                        os.unlink(resume_path)
                    except:
                        pass

# Footer
st.markdown("---")
st.markdown("**Powered by:**")
st.markdown("- 🤖 CrewAI for multi-agent orchestration")
st.markdown("- ⚡ Google Gemini for AI processing")
st.markdown("- 🔍 SerperDev for web searching")
st.markdown("- 🎨 Streamlit for the user interface")
st.markdown("- 📄 PyPDF2 for PDF processing")

# Installation instructions
with st.expander("📦 Installation Requirements"):
    st.code("""
# Install required packages:
pip install crewai crewai-tools streamlit python-dotenv PyPDF2 nest-asyncio

# Set environment variables:
export GOOGLE_API_KEY="your_gemini_api_key"
export SERPER_API_KEY="your_serper_api_key"
    """, language="bash")

# Enhanced troubleshooting section
with st.expander("🛠️ Troubleshooting"):
    st.markdown("""
    **Common Issues:**
    
    1. **503 Model Overloaded Error**: 
       - This is Google's most common error during peak hours
       - The app automatically retries with backoff delays
       - Try during off-peak hours (early morning/late evening)
       - Wait 5-10 minutes and try again
    
    2. **Rate Limit Exceeded**: 
       - You've hit the API usage limits
       - Wait 1-5 minutes before retrying
       - Consider using during off-peak hours
    
    3. **Event Loop Error**: 
       ```bash
       pip install nest-asyncio
       ```
    
    4. **API Key Issues**: 
       - Ensure your environment variables are set correctly
       - `GOOGLE_API_KEY` or `GEMINI_API_KEY` for Google Gemini
       - `SERPER_API_KEY` for web search functionality
    
    5. **File Processing Issues**: 
       - Ensure your resume is in a supported format (PDF, MD, TXT)
       - Try a smaller file if processing fails
       - Check that the file is not corrupted
    
    6. **Network Issues**: 
       - Stable internet connection required
       - Corporate firewalls may block API calls
    
    **Peak Usage Hours:**
    - Avoid 9 AM - 5 PM in your timezone
    - Best times: Early morning (6-8 AM) or late evening (9-11 PM)
    """)
import os
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, user_info, user_name):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### CANDIDATE INFORMATION:
            Name: {user_name}
            Background: {user_info}

            ### INSTRUCTION:
            You are {user_name}, writing a professional cold email to apply for the job mentioned above.
            
            Write a compelling cold email that:
            1. Has a strong opening that grabs attention
            2. Shows genuine interest in the specific role and company
            3. Highlights 2-3 most relevant skills/experiences that match the job requirements
            4. Demonstrates concrete value you can bring to their team
            5. Ends with a clear call-to-action
            6. Keep it concise and readable (3-4 short paragraphs, max 200 words)
            7. Use a professional but warm tone
            
            Format the email properly with:
            - Professional greeting
            - Clear paragraph breaks
            - Professional closing with your name
            
            Do NOT include:
            - Subject line
            - Your contact information (email/phone)
            - Generic statements
            - Overly formal language
            
            Make it personal, enthusiastic, and authentic.
            
            ### EMAIL:

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job), 
            "user_info": user_info,
            "user_name": user_name
        })
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
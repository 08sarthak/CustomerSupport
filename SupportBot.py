# Warning control
import warnings
warnings.filterwarnings('ignore')

import markdown2
from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool, DOCXSearchTool, TXTSearchTool, PDFSearchTool
from IPython.display import Markdown
import os
from utils import get_openai_api_key

openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

customer_sentiment_analysis_agent = Agent(
    role="Customer Sentiment Analysis Agent",
    goal="Accurately analyze and interpret the emotional tone of customer messages.",
    backstory=(
        "You work at {company} ({URL}) and your primary task is to analyze "
        "the sentiment of customer interactions to determine their emotional state. "
        "You need to quickly and accurately identify whether the customer is frustrated, "
        "neutral, or happy to ensure their query is handled appropriately. "
        "Your analysis will help route the customer to the right support level, "
        "improving overall customer satisfaction and support efficiency."
    ),
    allow_delegation=False,
    verbose=True
)


customer_query_analysis_agent = Agent(
    role="Customer Query Analysis Agent",
    goal="Thoroughly understand and categorize customer queries.",
    backstory=(
        "You work at {company} ({URL}) and your responsibility is to analyze "
        "customer queries to understand their nature and categorize them correctly. "
        "You must ensure that each query is understood correctly and comprehensively. "
        "for prompt and accurate resolution. Your work is crucial in maintaining the efficiency "
        "of the support system and ensuring that customers receive timely and appropriate responses."
    ),
    allow_delegation=False,
    verbose=True
)


senior_support_representative_agent = Agent(
    role="Senior Support Representative",
    goal="Be the most friendly and helpful support representative in your team.",
    backstory=(
        "You work at {company} ({URL}) and are now working on providing "
        "support to customer for your company. "
        "You need to make sure that you provide the best support! "
        "Make sure to provide full complete answers, and make no assumptions. "
        "Your expertise and friendly approach will ensure customer satisfaction and loyalty."
    ),
    allow_delegation=False,
    verbose=True
)


support_quality_assurance_agent = Agent(
    role="Support Quality Assurance Agent",
    goal="Ensure the highest quality of customer support interactions by monitoring and providing feedback.",
    backstory=(
        "You work at {company} ({URL}) and your role is to review support interactions "
        "to ensure they meet the company's quality standards. "
        "You will provide constructive feedback to support representatives to help them improve their performance. "
        "Your goal is to ensure consistent, high-quality support that enhances customer satisfaction and trust."
    ),
    allow_delegation=False,
    verbose=True
)

URL="https://www.dell.com/support/home/en-in"
docs_scrape_tool = ScrapeWebsiteTool(URL)
#docx_search_tool = DOCXSearchTool()
#txt_search_tool = TXTSearchTool()
#pdf_search_tool = PDFSearchTool()


sentiment_analysis_task = Task(
    description=(
        "A customer has reached out with an important query:\n"
        "{inquiry}\n\n"
        "Analyze the emotional tone of the customer's message to determine "
        "whether they are frustrated, neutral, or happy."
        "Use your sentiment analysis tools to provide a detailed sentiment report."
    ),
    expected_output=(
        "Give a short analysis on the tone of the customer."
        "Give key points on the best way to handle the customer according to their sentiment "
    ),
    agent=customer_sentiment_analysis_agent,
    async_execution=True
)

query_analysis_task = Task(
    description=(
        "A customer has reached out with an important query:\n"
        "{inquiry}\n\n"
        "Analyze the customer's query to understand its nature and categorize it correctly."
        "Provide detailed information about the query, including the main topic, any subtopics, and the customer's intent."
    ),
    expected_output=(
        "A thorough query analysis report that categorizes the customer's inquiry.\n"
        "The report should include the main topic of the query, subtopics, the customer's intent, and any specific details that "
        "will help the support representative provide a complete and accurate response."
    ),
    agent=customer_query_analysis_agent,
    async_execution=True
)


inquiry_resolution_task =  Task(
    description=(
        "customer just reached out with a query:\n"
	    "{inquiry}\n\n"
		"Make sure to use everything you know "
        "to provide the best support possible."
        "Use the companies guide to solve the issue(guide)"
		"You must strive to provide a complete "
        "and accurate response to the customer's inquiry."
    ),
    expected_output=(
	    "A detailed, informative response to the "
        "customer's inquiry that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
		"leaving no questions unanswered, and maintain a helpful and friendly "
		"tone throughout."
         "Do not include and signing off or closing text."
    ),
	tools=[docs_scrape_tool],
    context=[sentiment_analysis_task, query_analysis_task],
    agent=senior_support_representative_agent
)

quality_assurance_task =  Task(
    description=(
        "Review the response drafted by the Senior Support Representative for customer's inquiry. "
        "Ensure that the answer is comprehensive, accurate, and adheres to the "
		"high-quality standards expected for customer support.\n"
        "Verify that all parts of the customer's inquiry "
        "have been addressed "
		"thoroughly, with a helpful and friendly tone.\n"
        "Check for references and sources used to "
        " find the information, "
		"ensuring the response is well-supported and "
        "leaves no questions unanswered."
    ),
    expected_output=(
        "A final, detailed, and informative response "
        "ready to be sent to the customer.\n"
        "This response should fully address the "
        "customer's inquiry, incorporating all "
		"relevant feedback and improvements.\n"
		"Don't be too formal, we are a chill and cool company "
	    "but maintain a professional and friendly tone throughout."
        "Do not include and signing off or closing text."
    ),
    context=[sentiment_analysis_task, query_analysis_task, inquiry_resolution_task],
    agent=support_quality_assurance_agent
)

crew = Crew(
  agents=[customer_sentiment_analysis_agent, customer_query_analysis_agent, senior_support_representative_agent, support_quality_assurance_agent],
  tasks=[sentiment_analysis_task, query_analysis_task, inquiry_resolution_task, quality_assurance_task],
  verbose=2,
  memory=True
)

# Function to generate a blog post
def customer_support(msg,company,url):
    result = crew.kickoff(inputs={"company": company,"URL": url,"inquiry":msg})
    formatted_result = markdown2.markdown(result)  # Convert the result to Markdown format
    return formatted_result
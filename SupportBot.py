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

docs_scrape_tool = ScrapeWebsiteTool()
docx_search_tool = DOCXSearchTool()
txt_search_tool = TXTSearchTool()
pdf_search_tool = PDFSearchTool()

customer_sentiment_analysis_agent = Agent(
    role="Customer Sentiment Analysis Agent",
    goal="Accurately determine the emotional tone from customer communications.",
    backstory=(
        "At {company} ({URL}), you analyze customer interactions to identify their emotions. "
        "Quickly pinpoint if the customer feels frustrated, happy, or neutral. "
        "Your insights direct the inquiry to the appropriate support tier, boosting satisfaction and efficiency."
    ),
    allow_delegation=False,
    verbose=True
)



customer_query_analysis_agent = Agent(
    role="Customer Query Analysis Agent",
    goal="Precisely understand and classify customer inquiries.",
    backstory=(
        "You are tasked at {company} ({URL}) with dissecting customer queries to grasp and accurately categorize their nature. "
        "Your detailed analysis ensures queries are swiftly and effectively resolved, maintaining support system fluidity."
    ),
    allow_delegation=False,
    verbose=True
)


senior_support_representative_agent = Agent(
    role="Senior Support Representative",
    goal="Deliver exemplary customer support by leveraging comprehensive company guides without personalized headers or signatures.",
    backstory=(
        "At {company} ({URL}), you provide top-tier customer support. Utilize company guides to craft thorough, "
        "precise responses, focusing solely on the content of the answers without using the customer's name or signing off. "
        "Your commitment to clarity and content-focused responses drives customer loyalty and satisfaction."
    ),
    allow_delegation=False,
    verbose=True
)


support_quality_assurance_agent = Agent(
    role="Support Quality Assurance Agent",
    goal="Guarantee the supreme quality of customer support interactions by focusing on content quality without personalization.",
    backstory=(
        "Working at {company} ({URL}), your role is to ensure all customer support interactions meet the highest standards. "
        "By providing detailed feedback, you help refine the skills of support representatives, enhancing overall service quality."
    ),
    allow_delegation=False,
    verbose=True
)


sentiment_analysis_task = Task(
    description=(
        "Analyze the emotional tone of this customer message to guide response strategies:\n"
        "{inquiry}\n\n"
        "Utilize sentiment analysis tools for an accurate emotional assessment."
    ),
    expected_output=(
        "Report the detected sentiment (frustrated, neutral, happy) and suggest tailored handling strategies."
    ),
    agent=customer_sentiment_analysis_agent,
    async_execution=True
)


query_analysis_task = Task(
    description=(
        "Decompose this customer query to understand its nature and ensure correct categorization:\n"
        "{inquiry}\n\n"
        "Determine the main topics, subtopics, and the customer's intent for a precise support approach."
    ),
    expected_output=(
        "Provide a comprehensive report categorizing the query, including topics, subtopics, and customer intent."
    ),
    agent=customer_query_analysis_agent,
    async_execution=True
)


inquiry_resolution_task = Task(
    description=(
        "Respond to this customer query using the company's detailed guides for reference:\n"
        "{inquiry}\n\n"
        "Guide: {guide}\n"
        "Your response must be comprehensive, focusing solely on the technical or factual content required to resolve the query. "
        "Avoid personalizing the response with the customer's name or adding any sign-off messages."
    ),
    expected_output=(
        "A detailed response that directly addresses all technical or factual aspects of the inquiry, "
        "referenced with the applicable guide sections. Ensure the response is focused entirely on providing "
        "solutions without any personalization or sign-off."
    ),
	tools=[docs_scrape_tool,pdf_search_tool,txt_search_tool,docx_search_tool],
    context=[sentiment_analysis_task, query_analysis_task],
    agent=senior_support_representative_agent
)

quality_assurance_task = Task(
    description=(
        "Review and refine this draft response prepared for a customer, ensuring it meets our high standards:\n"
        "Verify the response is comprehensive, well-supported, and maintains our friendly yet professional tone."
    ),
    expected_output=(
        "Finalize the response ensuring it’s informative, fully addresses the inquiry, and strictly focuses on solution content. "
        "Confirm that the response includes no personalization or closing remarks, maintaining a professional and focused tone."
    ),
    context=[sentiment_analysis_task, query_analysis_task, inquiry_resolution_task],
    agent=support_quality_assurance_agent
)

crew = Crew(
  agents=[customer_sentiment_analysis_agent, customer_query_analysis_agent, senior_support_representative_agent, support_quality_assurance_agent],
  tasks=[sentiment_analysis_task, query_analysis_task, inquiry_resolution_task, quality_assurance_task],
  verbose=2,
  memory=True,
  embedder={
      "provider": "openai",
      "config":{
          "model": 'text-embedding-3-small'
          }
  }
)

# Function to generate a blog post
def customer_support(msg,company,url,file_loc):
    result = crew.kickoff(inputs={"company": company,"URL": url,"inquiry":msg,"guide":file_loc})
    formatted_result = markdown2.markdown(result)  # Convert the result to Markdown format
    return formatted_result



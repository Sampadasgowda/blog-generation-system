import os
import time
import wikipediaapi
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# Set your OpenAI API Key
os.environ[
    "OPENAI_API_KEY"] = "YOUR_API_KEY"  # Replace with your actual API key


# Function to search Wikipedia with a proper user-agent
def search_wikipedia(topic):
    """Search Wikipedia and return a summary of the topic."""
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='MyCustomAgent/1.0 (https://mywebsite.com; myemail@example.com)'  # Replace with your details
    )
    page = wiki_wiki.page(topic)
    if page.exists():
        return page.summary[:500]  # Return the first 500 characters of the summary
    else:
        return "Topic not found on Wikipedia."


# Wikipedia tool
wikipedia_tool = Tool(
    name="Wikipedia",
    func=search_wikipedia,
    description="Use this tool to get summaries from Wikipedia."
)

# Initialize ChatOpenAI with the valid API key
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)


# Blog generation function
def generate_blog(topic):
    """Generate a blog based on the given topic."""
    research_summary = search_wikipedia(topic)
    blog_prompt = f"""
    Generate a blog with the following structure:

    Heading: {topic}

    Introduction: Provide an engaging introduction to the topic.

    Content: Present detailed and informative content supported by the following research:
    {research_summary}

    Summary: Summarize the main points covered in the blog.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Use the invoke method with the blog_prompt as a string
            blog_content = llm.invoke(blog_prompt)
            return blog_content  # Return the generated blog content
        except Exception as e:
            print(f"Error generating blog: {e}")
            if "Rate limit exceeded" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Unable to generate blog.")
                    return "Blog generation failed due to rate limits."


# Test the blog generation function
topic = "Artificial Intelligence"
blog = generate_blog(topic)
print(blog)

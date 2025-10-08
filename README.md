# Interview Agent

**Interview Agent** is an AI-powered multi-agent system that operates in two distinct modes:

1. **Interview Mode**: The agent conducts insightful interviews with users, collecting detailed professional profiles and evaluating their skills and experience.
2. **Human Resources Mode**: The agent helps HR professionals find the best candidates for hiring based on user profiles and job requirements.

This project aims to provide a custom implementation without relying on complex libraries, focusing on creating a unique and flexible experience for collecting and evaluating data.

---

## **Features**

- **Interview Mode**:
  - Collects detailed information from users through targeted questions.
  - Validates and evaluates user claims.
  - Builds a comprehensive user profile and assesses their expertise level.

- **Human Resources Mode**:
  - Searches and matches candidates based on HR queries.
  - Uses web search, similarity searches, and internal filters to identify the best candidates.

- **Custom Tools**:
  - **Tavily**: Used for web search.
  - **PostgreSQL**: Used for storing user data and profiles.
  - **Chromadb**: Used for vector search and storing embeddings.

---

## **Tech Stack**

- **Python 3.x**
- **Streamlit**: For the web-based user interface.
- **Tavily API**: For performing web searches.
- **ChromaDB**: For vector-based search and storing vector data.
- **PostgreSQL**: For structured data storage.
- **OpenAI API**: For NLP tasks and interacting with large language models (LLMs).
- **dotenv**: For managing environment variables.

---

## **Setup Instructions**

### 1. Clone the repository:

```bash
git clone https://github.com/yourusername/petaproc-people-agent.git
cd petaproc-people-agent
```
## 2. Install dependencies:

Make sure you have Python 3.x installed. Then, install the required Python packages:
```bash
pip install -r requirements.txt
```
## 3. Environment Configuration:

Create a .env file in the root of your project and add the following environment variables:
```bash
GAP_GAP_API_KEY=your_api_key_here
DATABASE_URL2=your_database_connection_string
TAVILY_API_KEY=your_tavily_api_key
```
## Usage

To run the project, simply execute the following command:
```bash
streamlit run app.py
```
This will start the Streamlit app, providing a web interface for interacting with the Agent.
How It Works
## Interview Mode

Initial Interaction: The agent starts by asking the user for information about their professional background, such as their name, field of expertise, years of experience, and key skills.

Expertise Evaluation: The agent then asks targeted, open-ended questions to evaluate the user's level of expertise in their field.

Profile Building: The agent constructs a professional profile using the gathered data, including the user's name, skills, experience, projects, and interests.

Data Validation: The agent validates the user’s claims by cross-referencing their information with online platforms (such as GitHub, LinkedIn).

Summary and Evaluation: Once all the necessary data is collected, the agent generates a summary of the user's profile and provides a professional evaluation of their expertise level.

## Human Resources Mode

Profile Search: When an HR professional queries the system, the agent performs a structured or semantic search to find profiles that match the criteria.

Candidate Matching: The agent can use internal databases (stored in PostgreSQL and ChromaDB) to find relevant profiles, as well as perform web searches if necessary using the Tavily API.

Ranking and Recommendations: Based on the search results, the agent ranks the best candidates and provides insights into their suitability for the position.



## Example Interaction in Interview Mode:

User: "Hi, my name is Kian Safari, an AI engineer with 5 years of experience at Nexus Innovations."

Agent: "Thank you for sharing your background, Kian! Can you tell me about the most significant challenges you've faced in deploying LLMs to production environments?"

User: "The main challenges were inference costs and managing model hallucinations."

Agent: "Interesting! Now, what are your key technical skills?"

User: "My main skills are Python and Deep Learning."

Agent: "Got it. Let’s finalize your profile... calling the profile creation tool now."

Contributing

We welcome contributions! Feel free to fork the repository, create a branch, and submit a pull request. If you find any issues or have suggestions, open an issue in the repository.

## Acknowledgments

OpenAI: For providing GPT-4 and other LLM capabilities.

Tavily: For the web search API.

ChromaDB: For storing vector embeddings and supporting efficient searches.

Streamlit: For building the web interface.

PostgreSQL: For structured data storage and management.

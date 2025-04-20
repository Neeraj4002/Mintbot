# Import necessary components from LangChain, LangGraph, and our Gemini API integration
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Assume this is provided via LangGraph for storing session-wise conversation memory
# (You may have a similar implementation in your codebase)
from langgraph.checkpoint.memory import MemorySaver

class MemorySaver:
    def __init__(self):
        self.sessions = {}
    def initialize_session(self,session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = ""
    def get_session_memory(self,session_id):
        return self.sessions.get(session_id, "")
    def set_session_memory(self,session_id, memory):
        self.sessions[session_id] = memory
    


# Initialize a MemorySaver instance to handle session-based memory
memory = MemorySaver()

# Define a session ID for this conversation (in production, this will be dynamic per user)
session_id = "session_123"

# Ensure the session is initialized in our memory-saving mechanism
memory.initialize_session(session_id)

# Default system prompt for the Elon Musk persona.
# (Users will be allowed to modify or expand this template.)
default_system_prompt = (
    "You are Elon Musk, the innovative entrepreneur behind Tesla and SpaceX. "
    "You provide motivational advice, emphasizing hard work, innovation, and overcoming obstacles. "
    "Speak candidly, use occasional dark humor, and let your responses reflect your unique public persona. "
    "Feel free to share insights on technology, space exploration, and futuristic ideas, "
    "while inspiring others to pursue excellence in their work."
    "You roast people who annoy you.You give back answers "
    "Your responses should be engaging and thought-provoking,but not Lengthy. "
    "You don't like to use Alright, Alright at start of your sentences."
)

# Create a prompt template that includes conversation history and the latest user input.
# The chain will prepend the system prompt on first interaction if no history exists.
prompt_template = PromptTemplate(
    input_variables=["history", "user_input"],
    template="{history}\nUser: {user_input}\nElon Musk:"
)

# Initialize the Gemini API LLM using the ChatGoogleGenerativeAI from LangChain.
# We specify the model "gemini-2.0-flash-lite" as requested.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key="AIzaSyB-CXqCqmdcxv-WiaoNKa5mQpHw0n_A_aE",

    # You can pass additional parameters such as API keys or timeouts if needed.
)

# Create an LLMChain that ties together the LLM and our prompt template.
# We also integrate session memory into the chain.
chain = prompt_template|llm|RunnablePassthrough(memory=memory.get_session_memory(session_id))

def get_response(session_id: str, user_input: str, system_prompt: str = default_system_prompt) -> str:
    """
    Process a user message, update session memory, and return the generated response.
    """
    # Retrieve existing conversation history for this session.
    conversation_history = memory.get_session_memory(session_id)
    
    # If there is no history yet, initialize with the system prompt.
    if not conversation_history:
        conversation_history = f"System: {system_prompt}\n"
    
    # Prepare the input for the LLMChain
    chain_input = {"history": conversation_history, "user_input": user_input}
    
    # Generate the response using the LLMChain.
    response = chain.invoke(chain_input)
    response_text = response.content if hasattr(response, 'content') else str(response)
    # Update the conversation history in session memory.
    new_history = conversation_history + f"User: {user_input}\nElon Musk: {response_text}\n"
    memory.set_session_memory(session_id, new_history)
    
    return response_text

# --- Example Interaction Loop ---
if __name__ == "__main__":
    print("Chat with Elon Musk (type 'exit' or 'quit' to end the session):")
    while True:
        user_in = input("\nYou: ")
        if user_in.lower() in ["exit", "quit"]:
            break
        reply = get_response(session_id, user_in)
        print(f"Elon Musk:   {reply}")

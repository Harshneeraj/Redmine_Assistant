# State imports
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
# Assistanat imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from datetime import datetime
# utilities
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
# tools
from tools import tool_list
# graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
# selenium

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)



class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    logged_in: bool
    project: str
    issue: str
    time_logged: bool

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            passenger_id = configuration.get("passenger_id", None)
            state = {**state, "user_info": passenger_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
    
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key="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")

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
           """You are a helpful Redmine assistant. 
        You can automate interactions with the Redmine web application using a set of tools powered by Selenium. 
        Use these tools only when relevant to perform project-related actions like logging in, listing projects, creating issues, or logging time.

        Available tools:

        1. login_to_redmine:
        - Logs into the Redmine system with stored credentials.

        2. list_projects:
        - Returns the list of projects in which the user can perform actions like log time or create issue.

        3. create_issue:
        - Creates a new Redmine issue under the given project.
        - Requires a valid project ID.

        4. list_issues:
        - Lists all issues assigned to the logged-in user in a project.

        5. log_time_to_selected_issue:
        - Logs time against a previously selected issue.
        - Adds a time entry comment and marks the state with `time_logged = True`.

        Only use tools when explicitly needed to complete the task.
        ASK THE USER FOR ANY MISSING INFORMATION."""
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

llm_tools = tool_list
part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(llm_tools)

builder = StateGraph(State)


# Define nodes: these do the work
builder.add_node("assistant", Assistant(part_1_assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(llm_tools))
# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
part_1_graph = builder.compile(checkpointer=memory)

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        # "passenger_id": "3442 587242",
        # Checkpoints are accessed by thread_id
        "thread_id": 1,
    }
}

if __name__ == "__main__":
    _printed = set()
    while True:
        # This is a blocking call that will wait for the user to enter a question
        # and then return the result.
        user_input = input("User Input: ")
        if user_input.lower() == "exit":
            break
        events = part_1_graph.stream(
            {"messages": ("user", user_input)}, config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed)
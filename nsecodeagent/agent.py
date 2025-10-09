from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from google.adk.tools import google_search
import sys
sys.path.append("../stockutils")
from stockutils import nse

APP_NAME = "stock_app"
USER_ID = "1234"
SESSION_ID = "session1234"
load_dotenv()
root_agent = Agent(
    model='gemini-2.0-flash',
    name='stock_agent',
    instruction= """
       You are an agent that finds correct NSE (National Stock Exchange ,India) NSE codes from the company name given as input.
       Input name may have spelling mistake, abbreviations etc. Sometimes NSE code itself may be given as input name
       .Input is a comma seperated list of company names 
       Important : Your response must be a valid Json matching the following structure
       {
       {Name: Name of the company1 given as input
        Code: NSE Code for the company1},
        {Name: Name of the company2 given as input
        Code: NSE Code for the company2},
        }
        if the code could not be found Code must be ""
    """,

    description='This agent finds the NSE codes for the company given as input.',
    tools=[google_search] # You can add Python functions directly to the tools list; they will be automatically wrapped as FunctionTools.
)


# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        print(event.author)
        if event.content and event.content.parts:
         if event.get_function_calls():
             print("  Type: Tool Call Request")
             calls = event.get_function_calls()
             if calls:
              for call in calls:
               tool_name = call.name
               arguments = call.args # This is usually a dictionary
               print(f"  Tool: {tool_name}, Args: {arguments}")
         elif event.get_function_responses():
             print("  Type: Tool Result")
             tool_result_print(event)
         elif event.content.parts[0].text:
             if event.partial:
                 print("  Type: Streaming Text Chunk")
             else:
                 print("  Type: Complete Text Message")
                 print(event.content.parts[0].text)
         else:
             print("  Type: Other Content (e.g., code result)")
        if event.actions and event.actions.state_delta:
         print(f"  State changes: {event.actions.state_delta}")
        print ("************************")
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
            return(final_response)
    print(len(session.events))
    print(session.app_name)


def tool_result_print(event):
    responses = event.get_function_responses()
    if responses:
     for response in responses:
        tool_name = response.name
        result_dict = response.response # The dictionary returned by the tool
        print(f"  Tool Result: {tool_name} -> {result_dict}")


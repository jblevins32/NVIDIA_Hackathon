import yaml
import os
import traceback
from io import StringIO
from contextlib import redirect_stdout
import random
import re


import langchain
from langchain_ollama import ChatOllama
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

class LLM_Solver():
    """
    A class that provides functionality for interacting with a language model (LLM) to assist with quantitative analysis
    and code execution. The LLM can generate Python code, execute it, and return the results to help with reasoning tasks.
    """
    
    def __init__(self):
        """
        Initializes the LLM_Solver object by loading configuration settings and initializing the LLM model.
        Sets the default system prompt, model parameters, and temperature for LLM.
        """
        
        self.default_filter_prompt = 'Filter the text based on the 3D referring expression.'
        self.default_expression_query = '3D Referring Expression: Find the chair closest to the door.'
        
        self.default_system_prompt = """
                You are an AI assistant with a Python interpreter. When quantitative analysis or code execution is required for assisting your reasoning, you may generate Python code. 
                Generated code should always include necessary imports and provide output relevant to the task.
                If code is generated, make sure it begins with ```python and it ends using ```.
                If there’s an error during execution, I will return the error message for you to adjust the code and try again.
                After you generate code, I will run it and input it into the next query I submit to you. At which point, 
                if you are satisfied with your answer after, and only after, you have received the code execution results, output "DONE: ANSWER" and provide the answer from the code execution.
        """
        self.default_filter_system_prompt = """You are a filtering assistant designed to process object data for solving 3D Referring Expressions. 
          You will receive a list of objects with their properties, including `InstanceID`, `class`, `X_location`, and `Y_location`. 
          Your task is to filter the list and output only the objects necessary to solve the given 3D Referring Expression.
        
          Follow these rules:
            1. Carefully analyze the 3D Referring Expression provided in the user prompt to identify the objects relevant to solving it.
            2. Retain only the objects that match the criteria or are directly referenced or necessary to compute the relationship specified in the expression.
            3. Remove all other objects from the list.
            4. Output only the filtered list of objects and their data in the same format as provided.
            5. Do not include any explanations, comments, or additional information in your output.
        
          The possible object classes you may encounter are:
            - 0: person
            - 1: bicycle
            - 2: car
            - 3: motorcycle
            - 4: airplane
            - 5: bus
            - 6: train
            - 7: truck
            - 8: boat
            - 9: traffic light
            - 10: fire hydrant
            - 11: stop sign
            - 12: parking meter
            - 13: bench
            - 14: bird
            - 15: cat
            - 16: dog
            - 17: horse
            - 18: sheep
            - 19: cow
            - 20: elephant
            - 21: bear
            - 22: zebra
            - 23: giraffe
            - 24: backpack
            - 25: umbrella
            - 26: handbag
            - 27: tie
            - 28: suitcase
            - 29: frisbee
            - 30: skis
            - 31: snowboard
            - 32: sports ball
            - 33: kite
            - 34: baseball bat
            - 35: baseball glove
            - 36: skateboard
            - 37: surfboard
            - 38: tennis racket
            - 39: bottle
            - 40: wine glass
            - 41: cup
            - 42: fork
            - 43: knife
            - 44: spoon
            - 45: bowl
            - 46: banana
            - 47: apple
            - 48: sandwich
            - 49: orange
            - 50: broccoli
            - 51: carrot
            - 52: hot dog
            - 53: pizza
            - 54: donut
            - 55: cake
            - 56: chair
            - 57: couch
            - 58: potted plant
            - 59: bed
            - 60: dining table
            - 61: toilet
            - 62: tv
            - 63: laptop
            - 64: mouse
            - 65: remote
            - 66: keyboard
            - 67: cell phone
            - 68: microwave
            - 69: oven
            - 70: toaster
            - 71: sink
            - 72: refrigerator
            - 73: book
            - 74: clock
            - 75: vase
            - 76: scissors
            - 77: teddy bear
            - 78: hair drier
            - 79: toothbrush
        
          Your goal is to ensure the filtered list includes just enough data to accurately solve the 3D Referring Expression, no more and no less. Be precise and concise."""
        self.max_retries = 3 # defines number of max code retries the LLM agent can take before stopping
        self._get_config()
        self._init_llm()
        self._init_app()
        self._init_filter_llm()
        self._init_filter_app()

    @staticmethod
    def _load_yaml_config(file_path):
        """
        Loads a YAML configuration file from the specified file path.

        Args:
            file_path (str): The path to the YAML configuration file.

        Returns:
            dict: A dictionary containing the configuration data from the YAML file.
        """
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def _get_thread_id(self,file_path):
        """
        Retrieves and updates the thread_id based on the configuration file.
    
        If the thread_id is 'random', it generates a new random thread_id.
        If the thread_id is 'same', it reuses the last saved thread_id.
        
        Args:
            file_path (str): The path to the YAML configuration file.
    
        Returns:
            str: The thread_id as a string.
        """
        try:
            # Load the YAML file
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Check if the thread_id is set to "random" or "same"
            if 'thread_id' not in config:
                raise KeyError("thread_id parameter not found in the configuration file.")
            
            if config['thread_mode'] == 'random':
                # Generate a new random thread_id (integer converted to string)
                new_thread_id = str(random.randint(1000, 9999))  # Adjust range as needed
                config['thread_id'] = new_thread_id
            elif config['thread_mode'] == 'same':
                # Use the last used thread_id (which should already be in the file)
                if 'last_thread_id' not in config:
                    raise KeyError("last_thread_id parameter not found for 'same' thread_id.")
                new_thread_id = config['last_thread_id']
            else:
                raise ValueError("Invalid value for thread_id. It should be 'random' or 'same'.")
            
            # Save the updated YAML file
            with open(file_path, 'w') as file:
                yaml.safe_dump(config, file)
            
            # Store the new thread_id as the last used thread_id for future reference
            config['last_thread_id'] = new_thread_id
            with open(file_path, 'w') as file:
                yaml.safe_dump(config, file)
            
            print(f"Using thread_id: {new_thread_id}")
            return new_thread_id
        
        except (yaml.YAMLError, FileNotFoundError) as e:
            print(f"Error reading YAML file: {e}")
        except (KeyError, ValueError) as e:
            print(f"Error updating thread_id: {e}")


    def _get_config(self):
        """
        Loads the configuration for the LLM. This includes loading the system prompt, model name, and temperature from
        a configuration file if it exists, or setting them to default values if the configuration file is not found.

        Sets the following instance variables:
            - system_prompt: The system prompt string for the LLM.
            - model: The model name for the LLM.
            - temperature: The temperature for the LLM, controlling randomness of outputs.
        """
        llm_config_path = "llm_config.yaml"
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the full path to the YAML file
        yaml_path = os.path.join(script_dir, llm_config_path)
        if os.path.exists(yaml_path):
            llm_config = self._load_yaml_config(yaml_path)
        
            self.system_prompt = llm_config.get('system_prompt', self.default_system_prompt)
            self.model = llm_config.get('model', 'llama3.2')
            self.temperature = llm_config.get('temperature',0)
            self.filter_prompt = llm_config.get('filter_prompt', self.default_filter_prompt)
            self.filter_system_prompt = llm_config.get('filter_system_prompt',self.default_filter_system_prompt)
            self.expression_query = llm_config.get('expression_query',self.default_expression_query)
            self.thread_id = self._get_thread_id(llm_config_path)
        else:
            print(f'No file called {llm_config_path} in current directory. Setting default parameters')
            
            self.system_prompt = self.default_system_prompt
            self.model = 'llama3.2'
            self.temperature = 0
            self.filter_prompt = self.default_filter_prompt
            self.filter_system_prompt = self.default_filter_system_prompt
            self.expression_query = self.default_expression_query
            self.thread_id = 'abc134'
        print(self.system_prompt)

    def _init_filter_llm(self):
        """
        Initializes the LLM model that will handle only filtering using the parameters defined in the configuration (model name, temperature).

        This method is used to set up the LLM model that will be used for generating code or reasoning based on input.
        """
        self.filter_llm = ChatOllama(
            model=self.model,
            temperature=self.temperature
        )

    def _init_llm(self):
        """
        Initializes the LLM model using the parameters defined in the configuration (model name, temperature).

        This method is used to set up the LLM model that will be used for generating code or reasoning based on input.
        """
        # Initialize LLM
        self.llm = ChatOllama(
            model=self.model,
            temperature=self.temperature # ranges from 0 to 1
        )
        
    @staticmethod
    def _execute_python_code(code:str)->str:
        """
        Executes Python code provided in a string and captures any output or errors that occur during execution.

        Args:
            code (str): A string of Python code to execute.

        Returns:
            str: The output from the code execution, or an error message if the execution fails.
        """
        try:
            # Capture standard output
            f = StringIO()
            with redirect_stdout(f):
                exec(code,{})
    
            # Return captured output
            return f.getvalue() if f.getvalue() else "Code executed without output."
        except:
            return f'Execution error: {traceback.format_exc()}'

    
    def _call_model(self,state: MessagesState):
        """
        Calls the LLM model with a given state and generates a response.

        Args:
            state (MessagesState): The current state of the model interaction, which includes messages or context.

        Returns:
            dict: A dictionary containing the generated response from the LLM model.
        """
        chain = self.prompt_template | self.llm
        response = chain.invoke(state)
        return {"messages": response}

    def _call_filter_model(self,state: MessagesState):
        """
        Calls the filter LLM model with a given state and generates a response.

        Args:
            state (MessagesState): The current state of the model interaction, which includes messages or context.

        Returns:
            dict: A dictionary containing the generated response from the LLM model.
        """
        filter_chain = self.filter_prompt_template | self.filter_llm
        filter_response = filter_chain.invoke(state)
        return {"messages": filter_response}
    
    @staticmethod
    def extract_python_code(response):
        """
        Extracts Python code from the response, handling variations in code block formatting.

        Args:
            response (dict): The response object containing the messages.

        Returns:
            str: The extracted Python code, or None if no code block is found.
        """
        # Check if the messages list exists and is non-empty
        # Check if the messages list exists and is non-empty
        if 'messages' in response and len(response['messages']) > 0:
            # Extract the content from the last message
            last_message = response['messages'][-1]
            
            # Ensure the content is within the AIMessage and check the structure
            if 'content' in last_message:
                content = last_message['content']
                content = content.strip()

                # Regex to match Python code blocks
                pattern = r'```[ ]*\n?python[ ]*\n(.*?)\n```'  # Handles separate lines for ``` and python

                # Search for the code block using regex, matching across multiple lines
                match = re.search(pattern, content, re.DOTALL)

                if match:
                    # If a match is found, return the captured code
                    return match.group(1).strip()

        # Return None if no code block is found
        return None

    def _init_app(self):
        """
        Initializes the app by setting up a tool for executing Python code, defining a prompt template, and creating a 
        state graph for managing the flow of the application.

        Sets up the following components:
            - Tool for executing Python code (using the _execute_python_code method).
            - Chat prompt template for the LLM model.
            - Workflow for managing the state and flow of the model interaction.
        """
        self.python_executor = Tool(name='PythonExecutor',
                      func=self._execute_python_code,
                      description='Executes Python code and returns the output or error.'
                      )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    f"{self.system_prompt}",
                ),
                MessagesPlaceholder(variable_name='messages'),
            ]
        )
        # Define a new graph
        self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow.add_edge(START, "model")
        self.workflow.add_node("model",self._call_model)
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)

    def _init_filter_app(self):
        """
        Initializes the filter app by defining a prompt template, and creating a 
        state graph for managing the flow of the application.

        Sets up the following components:
            - Chat prompt template for the filter LLM model.
            - Workflow for managing the state and flow of the model interaction.
        """

        self.filter_prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    f"{self.filter_system_prompt}",
                ),
                MessagesPlaceholder(variable_name='messages'),
            ]
        )
        # Define a new graph
        self.filter_workflow = StateGraph(state_schema=MessagesState)
        self.filter_workflow.add_edge(START, "model")
        self.filter_workflow.add_node("model",self._call_filter_model)
        filter_memory = MemorySaver()
        self.filter_app = self.filter_workflow.compile(checkpointer=filter_memory)

    def run(self, input_string, expression_query):
        config = {"configurable": {"thread_id": f"{self.thread_id}"}}
        filter_config = {"configurable": {"thread_id": f"{random.randint(1000, 9999)}"}} 
        print('Object Info received')
        # Exit if user types 'exit'
        if expression_query != "":
            self.expression_query = expression_query
        if self.expression_query.lower() == 'exit':
            print('Exiting Dialogue.')
            return

        input_messages = [HumanMessage(self.expression_query+'\n'+self.filter_prompt+'\n Here is the sensor data to use to solve the 3D referring expression:'+input_string)]
        print(f"You: {input_messages[-1].content}")
        
        response = self.filter_app.invoke({'messages': input_messages},filter_config)

        print("\n\nResponse:",response['messages'][-1].content,'\n')
        filtered_string = response['messages'][-1].content
        
        input_messages = [HumanMessage(self.expression_query+'\nFiltered Data Observed:\n'+filtered_string+'\nNow you can output Python code to calculate your response to assist your decision-making.')]
        print(f"You: {input_messages[-1].content}")

        response = self.app.invoke({'messages': input_messages},config)
        print("\n\nResponse:",response['messages'][-1].content,'\n')

        # Check for Python code blocks in the LLM response
        if "```python" in response['messages'][-1].content:
            code_snippet = response['messages'][-1].content.split("```python")[1].split("```")[0].strip()
            retries = 0
            while retries < self.max_retries:
                print('\nExecuting code snippet:\n', code_snippet)
                try:
                    # Execute the code
                    execution_result = self.python_executor.run(code_snippet)
        
                    # Append execution results to continue the conversation
                    print('\nExecution Result:', execution_result)
                    result_context = (f"Your Code Execution Result: {execution_result}\n")
                    
                    # Pass the result back as context to refine or complete the response
                    response = self.app.invoke({'messages': [HumanMessage(result_context)]}, config)
                    print('\nLLM Response after execution:', response['messages'][-1].content, '\n')

                    # Update the code snippet if the LLM provided refined code
                    if "```python" in response['messages'][-1].content:
                        code_snippet = response['messages'][-1].content.split("```python")[1].split("```")[0].strip()
                    else:
                        print('No refined code provided, exiting refinement loop.')
                        break
                        
                except Exception as e:
                    retries += 1
                    # Provide erro to LLM for feedback
                    print(f'\nError during code execution (Attempt {retries}/{self.max_retries}): {e}')
                    error_context = f"Error during code execution: {str(e)}"
                    response = self.app.invoke({'messages': [HumanMessage(error_context)]},config)
                    print('\nLLM Response after error: ', response['messages'][-1].content, '\n')
                    
                    # Update the code snippet if the LLM provided refined code
                    if "```python" in response['messages'][-1].content:
                        code_snippet = response['messages'][-1].content.split("```python")[1].split("```")[0].strip()
                    else:
                        print('No refined code provided, exiting refinement loop.')
                        break
                        
            if retries == self.max_retries:
                print('Max retries reached, exiting code execution loop.')    
        else:
            print('No code detected, ending dialogue.\n')

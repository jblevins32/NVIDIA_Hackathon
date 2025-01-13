import yaml
import os
import traceback
from io import StringIO
from contextlib import redirect_stdout

import os
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
        self.max_retries = 3 # defines number of max code retries the LLM agent can take before stopping
        self._get_config()
        self._init_llm()
        self._init_app()

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
        if os.path.exists(llm_config_path):
            llm_config = self._load_yaml_config(llm_config_path)
        
            self.system_prompt = llm_config.get('system_prompt', self.default_system_prompt)
            self.model = llm_config.get('model', 'llama3.2')
            self.temperature = llm_config.get('temperature',0)
            self.filter_prompt = llm_config.get('filter_prompt', self.default_filter_prompt)
            self.expression_query = llm_config.get('expression_query',self.default_expression_query)
            self.thread_id = llm_config.get('thread_id','abc120')
        else:
            print(f'No file called {llm_config_path} in current directory. Setting default parameters')
            
            self.system_prompt = self.default_system_prompt
            self.model = 'llama3.2'
            self.temperature = 0
            self.filter_prompt = self.default_filter_prompt
            self.expression_query = self.default_expression_query
            self.thread_id = 'abc134'
        print(self.system_prompt)

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
        chain = self.prompt | self.llm
        response = chain.invoke(state)
        return {"messages": response}

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

        self.prompt = ChatPromptTemplate.from_messages(
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

    def _run(self, input_string):
        config = {"configurable": {"thread_id": f"{self.thread_id}"}}
        print('Object Info received')
        # Exit if user types 'exit'
        if self.expression_query.lower() == 'exit':
            print('Exiting Dialogue.')
            return
        print('You: '+self.expression_query+'\n'+self.filter_prompt+'\n Here is the sensor data to use to solve the 3D referring expression:'+input_string)
        input_messages = [HumanMessage(self.expression_query+'\n'+self.filter_prompt+'\n Here is the sensor data to use to solve the 3D referring expression:'+input_string)]
        response = self.app.invoke({'messages': input_messages},config)
        print("\n\nResponse:",response['messages'][-1].content,'\n')
        filtered_string = response['messages'][-1].content
        
        print('You: '+self.expression_query+'\nFiltered Data Observed:\n'+filtered_string)
        input_messages = [HumanMessage(self.expression_query+'\nFiltered Data Observed:\n'+filtered_string+'/nNow you can output Python code to calculate your response to assist your decision-making.')]
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

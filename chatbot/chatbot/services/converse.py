import getpass
import os
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from datetime import datetime, timedelta
from enum import Enum

model = ChatMistralAI(model="mistral-large-latest")
os.environ["MISTRAL_API_KEY"] = getpass.getpass()

class Context(Enum):
    E= "Entry"
    C= "Checking"
    V= "Visualization"
    R="Reporting"
    F= "Foreign"
    
class Status(Enum):
    IN= "Initial"
    EN= "Engage"
    AL= "Alert"
    
class Starter:
    def __init__(self):
        self.model=model

    def opener(self):
        input = """
        Hi, My name is Trackio, Nice to Meet you! 😊
        I see this is your first time with us, we need to log your info into our database. Please provide us with the following details:
        1. Username 🧑‍💻
        2. Password 🔒
        3. Monthly Budget 💰
        4. Saving Cutoff (nominals) 📊
        """
        return input
    
    def converse_starter(self):
        input="""
        Yo, what do you want ?
        """
        return input
    
    def entry(self):
        input="""
        Got it, give me the number and it's category 😊"""
        return input
    
    
    def rerun(self, prev_context):
        prompt = f"""
        Based on the previous context, I need to proceed with the following tasks. Here is the past context:
        {prev_context}
        ask user to redo question the based on the past context
        """
        response = self.model.generate(prompt)
        return response
    
    def viz(self):
        input="""
        Give me what type of plot you want and the duration of data you want, this can be certain dates or today, this week, certain month etc 😊"""
        return input
        

class Extraction:
    def __init__(self):
        self.model=model
    
    def opener(self, input_text):
        prompt = f"""
            Given the following input text, extract the data for username, password, monthly budget, and saving cutoff.

            Input:
            {input_text}

            Extracted Information:
            1. Username:
            2. Password:
            3. Monthly Budget:
            4. Saving Cutoff:
            """
        response = self.model.generate(prompt)
        extracted_data = []
            
        lines = response.split('\n')
        for line in lines:
            if line.startswith("1. Username:"):
                extracted_data.append(line.split(":")[1].strip())
            elif line.startswith("2. Password:"):
                extracted_data.append(line.split(":")[1].strip())
            elif line.startswith("3. Monthly Budget:"):
                extracted_data.append(line.split(":")[1].strip())
            elif line.startswith("4. Saving Cutoff:"):
                extracted_data.append(line.split(":")[1].strip())
            else:
                return False  
        return extracted_data
    
    def mp_extraction(self, input_text):
        prompt = f"""
        Given the following input, classify it based on these topics

            Input:
            {input_text}
            
            Topics:
            Entry, Checking, Viz, or Report CSV
            """
        response = self.model.generate(prompt)
        
        # Map response to the Context Enum
        try:
            context = Context[response.upper()]
        except KeyError:
            context = None 
        return context
    
    def entry(self, input: str):
        prompt = f"""
        Extract the category and nominal value from the following text:
        
        Input: {input}
        
        The categories are: Food, Clothing, Rent, Transport
        Please return the output in the following format:
        {{'Category': <category>, 'Nominal': <nominal_value>}}

        Example: 
        Input: "I spend 20 ringgit for food just now"
        Output: {{'Category': 'Transport', 'Nominal': 5000}}
        """
        response = self.model.generate([prompt])
        
        # Parse the response (assuming the response is in the correct format)
        try:
            extracted_info = eval(response[0]['text'])  # Convert the response to a dictionary
            
            return extracted_info
        except Exception as e:
            return {"Error": f"Failed to extract information. Error: {str(e)}"}
    
    def viz(self, input: str) -> dict:
        # Define the prompt for the model
        prompt = f"""
        Extract the type of plot and the time range from here.

        Input: {input}

        time range = today, this week, last week, last month, and date range (e.g., 11/07/2023 to 12/07/2023)
        plot = bar, pie, line chart

        Please return the output in the following format:
        {{'timeRange': <time range>, 'Plot': <plot>}}

        Example: 
        Input: "Give me bar plot for last week expenses"
        Output: {{'Category': 'Entry', 'Nominal': 5000}}
        """
        
        # Get the current date
        now = datetime.now().date()
        
        # Generate a response using the model
        response = self.model.generate([prompt])
        
        try:
            # Safely evaluate the text output from the model
            extracted_info = eval(response[0]['text'])
            sign = extracted_info.get("timeRange")

            # Adjust the time range based on recognized keywords
            if sign == "today":
                extracted_info["timeRange"] = now
            elif sign == "this week":
                extracted_info["timeRange"] = now - timedelta(days=now.weekday())
            elif sign == "last week":
                extracted_info["timeRange"] = now - timedelta(days=7 + now.weekday())
            elif sign == "last month":
                extracted_info["timeRange"] = now.replace(day=1) - timedelta(days=1)
            elif "to" in sign:
                start_date_str, end_date_str = sign.split(" to ")
                start_date = datetime.strptime(start_date_str.strip(), '%m/%d/%Y').date()
                end_date = datetime.strptime(end_date_str.strip(), '%m/%d/%Y').date()
                extracted_info["timeRange"] = f"{start_date} to {end_date}"
            else:
                extracted_info["timeRange"] = f"Unknown time range: {sign}"
            
            return extracted_info
        
        except KeyError as e:
            return {"Error": f"Key error: {str(e)}"}
        
        except SyntaxError as e:
            return {"Error": f"Syntax error in response: {str(e)}"}
        
        except Exception as e:
            return {"Error": f"Failed to extract information. Error: {str(e)}"}
        
        
        
    
    
    
        

        
        
        
        



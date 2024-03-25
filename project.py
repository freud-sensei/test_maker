from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from pprint import pprint
from langchain.chains.openai_functions import create_structured_output_runnable
from typing import List

load_dotenv()


class SingleQuestion(BaseModel):
    question: str = Field(description="Nultiple choice questions")
    selection: List[str] = Field(description = "List of five selectable answers for each question")
    answer: str = Field(description="Correct answer for question, must be 'A', 'B', 'C', 'D' or 'E'")
    explanation: str = Field(description="Explanation on why the answer is correct for each question")
    
class Questionmaker(BaseModel):
    questions: List[SingleQuestion] = Field(description="List of {num_questions} questions")

model = ChatOpenAI(
    model="gpt-3.5-turbo", temperature=0, max_tokens=None)
template = "You are a study assistant which generates mulitple-choice questions for students.\nBy using [INPUT_DATA], make multiple choice questions in a structured format.\nYou must create a total of {num_questions} different questions.\nThe language must be in {language}.\n[INPUT_DATA]: {input_data}"

prompt = PromptTemplate.from_template(template)

chain = create_structured_output_runnable(Questionmaker, model, prompt)

with open("harry.txt", encoding='utf-8') as f:
    input_text = f.read()

def generate_question(input_text, language, num_questions):
    response = chain.invoke({"input_data": input_text, "language": language, "num_questions": num_questions})
    return response
        
pprint(generate_question(input_text, "English", 2))
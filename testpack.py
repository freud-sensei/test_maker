# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.chains.openai_functions import create_structured_output_runnable
from typing import List
import random
from pprint import pprint
import openai
import streamlit as st
from read_files import read_docx, read_pdf

load_dotenv()

class SingleQuestion(BaseModel):
    question: str = Field(description="Multiple choice questions")
    correct: str = Field(description = "The correct answer")
    incorrect: List[str] = Field(description = "List of incorrect answers")
    explanation: str = Field(description="Explanation on why the answer is correct for each question")   
    
class Questionmaker(BaseModel):
    questions: List[SingleQuestion] = Field(description="List of questions") 

template = '''
You are a study assistant which must generate unique {num_questions} multiple-choice questions for students.\n
By using [INPUT_DATA], make multiple choice questions in a structured format.\n
You must make one correct answer, and a maximum of four incorrect answers.\n
The language must be in {language}.\n
Tips: You must return {num_questions} questions, not more and not less.

[INPUT_DATA]:\n
{input_data}
'''

def generate_questionnaire(model_name, input_text, language, num_questions):
    try:
        if model_name == "GPT-4":
            model_ver = "gpt-4-0125-preview"
        elif model_name == "GPT-3.5":
            model_ver = "gpt-3.5-turbo-0125"

        model = ChatOpenAI(model=model_ver, temperature=1, max_tokens=None)
        prompt = PromptTemplate.from_template(template)
        chain = create_structured_output_runnable(Questionmaker, model, prompt)
        response = chain.invoke({"input_data": input_text, "language": language, "num_questions": num_questions})
        response_list = response.questions
        if len(response_list) < num_questions:
            st.write("인공지능의 한계로 설정하신 문제 수보다 적은 수의 문제가 출제되었습니다.")      
        
        random.shuffle(response_list)
        questionnaire = list()
        for question in response_list:        
            q_dict = dict()
            q_dict["question"] = question.question
            total_selections = 1 + len(question.incorrect)
            correct_index = random.randint(0, total_selections -1)
            q_dict["selection"] = question.incorrect
            while "" in q_dict["selection"]:
                q_dict["selection"].remove("")
            q_dict["selection"].insert(correct_index, question.correct)
            q_dict["correct"] = correct_index
            q_dict["explanation"] = question.explanation
            questionnaire.append(q_dict)    
        return questionnaire
    except openai.BadRequestError as e:
        st.write("파일에 문제가 있거나 내용이 너무 길어 문제를 생성할 수 없습니다.")
        st.write("새로고침한 후 다시 시도해보세요.")
        st.write(e)


if __name__ == "__main__":
    pprint(generate_questionnaire("GPT-4", read_docx("sample.docx"), "한국어", 5))

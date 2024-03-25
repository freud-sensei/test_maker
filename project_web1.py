import streamlit as st
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
    answer: str = Field(description="Correct answer for question")
    explanation: str = Field(description="Explanation on why the answer is correct for each question")
    
class Questionmaker(BaseModel):
    questions: List[SingleQuestion] = Field(description="List of {num_questions} questions")

model = ChatOpenAI(
    model="gpt-3.5-turbo", temperature=0, max_tokens=None)
template = "You are a study assistant which generates mulitple-choice questions for students.\nBy using [INPUT_DATA], make multiple choice questions in a structured format.\nYou must create a total of {num_questions} different questions.\nThe language must be in {language}.\n[INPUT_DATA]: {input_data}"

prompt = PromptTemplate.from_template(template)

chain = create_structured_output_runnable(Questionmaker, model, prompt)

@st.cache_resource
def generate_question(input_text, language, num_questions):
    response = chain.invoke({"input_data": input_text, "language": language, "num_questions": num_questions})
    return response
        
with open("neuro.txt",encoding='utf-8') as f:
    sample = f.read()
    
def callback():
    st.session_state.questionnaire = generate_question(st.session_state.input_text, st.session_state.language, st.session_state.num_questions).questions
    st.session_state.button_clicked = True
    
def callback2():
    st.session_state.button2_clicked = True
    
def callback3():
    st.session_state.button_clicked = False
    st.session_state.button2_clicked = False
    
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False
    
if "button2_clicked" not in st.session_state:
    st.session_state.button2_clicked = False

st.title("모의고사 자동제작 서비스")

if not st.session_state.button_clicked:
    with st.form("maker"):
        input_text = st.text_area("내용 입력", value=sample, key="input_text")
        language = st.radio("언어 선택", ["한국어", "English"], index=0, key="language")
        num_questions = st.slider("생성할 문제 수 설정 (인공지능의 한계로 더 적은 문제가 생성될 수 있음)", min_value=1, max_value=10, value=5, key="num_questions")
        st.form_submit_button("모의고사 생성하기", on_click=callback)

if st.session_state.button_clicked:
    answers = {}
    score = 0
    with st.form("main_quiz"):
        for idx, question in enumerate(st.session_state.questionnaire):
            answers[idx] = st.radio(
                f"{idx + 1}. {question.question}",
                [sel for sel in question.selection],
                index=0,
                key=f"question_{idx}"
            )
            if st.session_state.button2_clicked:
                if answers[idx] == question.answer:
                    st.write(f"정답입니다! {question.explanation}")
                    score += 1
                else:
                    st.write(f"오답입니다. 정답은 {question.answer}입니다. {question.explanation}")               
        if not st.session_state.button2_clicked:
            st.form_submit_button("제출하기", on_click=callback2)
        else:
            st.write(f"{len(st.session_state.questionnaire)}개 중 {score}개 맞추셨습니다.")
            st.form_submit_button("처음으로 돌아가기", on_click=callback3)
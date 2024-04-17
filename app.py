
import time
import streamlit as st
from code_editor import code_editor
import os
import streamlit as st
import vanna as vn
from dotenv import load_dotenv

from vanna.remote import VannaDefault

@st.cache_resource(ttl=3600)
def setup_connexion():
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
        
       


def setup_session_state():
    st.session_state["my_question"] = None


import streamlit as st
import vanna as vn


@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
    return vn.generate_questions()


@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
    return vn.generate_sql(question=question)


@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
    return vn.run_sql(sql=sql)


@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
    return vn.get_plotly_figure(plotly_code=code, df=df)


@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, df):
    vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
    vn.connect_to_sqlite('mydatabase.db')
    return vn.generate_followup_questions(question=question, df=df)

st.set_page_config(layout="wide")
setup_connexion()
vn = VannaDefault(model='axonic', api_key='794c9f61449042fcbd1570d595043395')
vn.connect_to_sqlite('mydatabase.db')

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Rerun", on_click=setup_session_state, use_container_width=True)

st.title("Sql AI")
st.sidebar.write(st.session_state)


def set_question(question):
    st.session_state["my_question"] = question


assistant_message_suggested = st.chat_message(
    "assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png"
)
if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        button = st.button(
            question,
            on_click=set_question,
            args=(question,),
        )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "Ask me a question about your data",
    )


if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if st.session_state.get("show_sql", True):
            assistant_message_sql = st.chat_message(
                "assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png"
            )
            assistant_message_sql.code(sql, language="sql", line_numbers=True)

        user_message_sql_check = st.chat_message("user")
        user_message_sql_check.write(f"Are you happy with the generated SQL code?")
        with user_message_sql_check:
            happy_sql = st.radio(
                "Happy",
                options=["", "yes", "no"],
                key="radio_sql",
                index=0,
            )

        if happy_sql == "no":
            st.warning(
                "Please fix the generated SQL code. Once you're done hit Shift + Enter to submit"
            )
            sql_response = code_editor(sql, lang="sql")
            fixed_sql_query = sql_response["text"]

            if fixed_sql_query != "":
                df = run_sql_cached(sql=fixed_sql_query)
            else:
                df = None
        elif happy_sql == "yes":
            df = run_sql_cached(sql=sql)
        else:
            df = None

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
                )
                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)

            code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

            if st.session_state.get("show_plotly_code", False):
                assistant_message_plotly_code = st.chat_message(
                    "assistant",
                    avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
                )
                assistant_message_plotly_code.code(
                    code, language="python", line_numbers=True
                )

            user_message_plotly_check = st.chat_message("user")
            user_message_plotly_check.write(
                f"Are you happy with the generated Plotly code?"
            )
            with user_message_plotly_check:
                happy_plotly = st.radio(
                    "Happy",
                    options=["", "yes", "no"],
                    key="radio_plotly",
                    index=0,
                )

            if happy_plotly == "no":
                st.warning(
                    "Please fix the generated Python code. Once you're done hit Shift + Enter to submit"
                )
                python_code_response = code_editor(code, lang="python")
                code = python_code_response["text"]
            elif happy_plotly == "":
                code = None

            if code is not None and code != "":
                if st.session_state.get("show_chart", True):
                    assistant_message_chart = st.chat_message(
                        "assistant",
                        avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
                    )
                    fig = generate_plot_cached(code=code, df=df)
                    if fig is not None:
                        assistant_message_chart.plotly_chart(fig)
                    else:
                        assistant_message_chart.error("I couldn't generate a chart")

                if st.session_state.get("show_followup", True):
                    assistant_message_followup = st.chat_message(
                        "assistant",
                        avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
                    )
                    followup_questions = generate_followup_cached(
                        question=my_question, df=df
                    )
                    st.session_state["df"] = None

                    if len(followup_questions) > 0:
                        assistant_message_followup.text(
                            "Here are some possible follow-up questions"
                        )
                        # Print the first 5 follow-up questions
                        for question in followup_questions[:5]:
                            time.sleep(0.05)
                            assistant_message_followup.write(question)

    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png"
        )
        assistant_message_error.error("I wasn't able to generate SQL for that question")

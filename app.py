import calendar  # Core Python Module
from datetime import datetime  # Core Python Module

import plotly.graph_objects as go  # pip install plotly
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu

import database as db  # local import

import json
import locale

# -------------- SETTINGS --------------
incomes = ["Salário", "Blog", "Outras Receitas"]
expenses = ["Feira", "Utilidades", "Carro", "Gasolina", "Outras Despesas","Luz","Água","Internet","Estudo"]
currency = "R$"
page_title = "Rastreador de receitas e despesas"
page_icon = ":money_with_wings:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# --- Português
locale.setlocale(locale.LC_ALL, "pt_BR")

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])


# --- DATABASE INTERFACE ---
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Cadastro", "Gráfico"],
    icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# --- INPUT & SAVE PERIODS ---
if selected == "Cadastro":
    st.header(f"Cadastro em: {currency}")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Selecione Mês:", months, key="month")
        col2.selectbox("Selecione Ano:", years, key="year")

        "---"
        with st.expander("Receitas"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
        with st.expander("Despesas"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
        with st.expander("Comentário"):
            comment = st.text_area("", placeholder="Digite um comentário aqui ...")

        "---"
        submitted = st.form_submit_button("Salvar")
        if submitted:
            period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            db.insert_period(period, incomes, expenses, comment)
            st.success("Dados salvos!")


# --- PLOT PERIODS ---
if selected == "Gráfico":
    st.header("Gráfico")
    with st.form("saved_periods"):
        period = st.selectbox("Selecione um período:", get_all_periods())
        submitted = st.form_submit_button("Gráfico do Período")
        if submitted:
            parsed_data = json.loads(db.get_period(period))
            # Agora parsed_data é uma lista de dicionários
            for period_data in parsed_data:
                incomes = period_data["incomes"]
                expenses = period_data["expenses"]
                comment = period_data["comment"]                

            # Create metrics
            total_income = sum(incomes.values())
            total_expense = sum(expenses.values())
            remaining_budget = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Receitas", f"{currency} {total_income}")
            col2.metric("Total Despesas", f"{currency} {total_expense}")
            col3.metric("Orçamento remanescente", f"{currency} {remaining_budget}")
            st.text(f"Comentário: {comment}")

            # Create sankey chart
            label = list(incomes.keys()) + ["Total Receita"] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            data = go.Sankey(link=link, node=node)

            # Plot it!
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)
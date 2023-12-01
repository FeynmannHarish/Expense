import streamlit as st
import sqlite3,warnings
import pandas as pd
import matplotlib.pyplot as plt
st.set_option('deprecation.showPyplotGlobalUse', False)
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
warnings.filterwarnings("ignore")
st.elements.utils._shown_default_value_warning=True

def clear():
    st.session_state.desc=""
    st.session_state.am=0.0

def statistics(df):
    summary_stats = pd.DataFrame({
    "Total Expenses": [df["amount"].sum()],
    "Average Expense": [df["amount"].mean()],
    "Maximum Expense": [df["amount"].max()],
    "Minimum Expense": [df["amount"].min()]
})
    
    return summary_stats

# Create a SQLite database or connect to an existing one
conn = sqlite3.connect('expenses.db')
cur = conn.cursor()

# Create an 'expenses' table if it doesn't exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date DATE,
        description TEXT,
        amount REAL
    )
''')

conn.commit()

# Streamlit App
st.title('Expense Tracking App')

# Sidebar for adding expenses
st.sidebar.header('Add New Expense')
date = st.sidebar.date_input('Date', pd.to_datetime('today'))


description=st.sidebar.text_input('Description',key='desc')
amount=st.sidebar.number_input('Amount', value=0.0,key='am')

if st.sidebar.button('Add Expense'):
    cur.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)", (date, description, amount))
    conn.commit()
    st.sidebar.success('Expense added successfully!')    

st.sidebar.button("Clear",on_click=clear)
# Display Expenses

expenses = pd.read_sql_query('SELECT * FROM expenses', conn)
expenses["date"] = pd.to_datetime(expenses["date"]).dt.date
st.dataframe(expenses)

if st.sidebar.button("Statistics"):
    st.dataframe(statistics(expenses[expenses["date"]==date]))

# Visualize Expenses
if not expenses.empty and st.sidebar.button("Visualize"):
    if description=="" and amount==0.0:
         st.header('Expense Visualization')
         st.subheader('Expense Breakdown')
         expenses = expenses[expenses["date"]==date]
         expense_sum = expenses['amount'].sum()
         st.write(f"Total Expenses: ${expense_sum:.2f}")
         category_expenses = expenses.groupby('description')['amount'].sum()
         plt.pie(category_expenses, labels=category_expenses.index, autopct='%1.1f%%')
         st.pyplot()
    else:
        st.header('Expense Visualization')
        st.subheader('Expense Breakdown')
        expense_sum = expenses['amount'].sum()
        st.write(f"Total Expenses: ${expense_sum:.2f}")
        category_expenses = expenses.groupby('description')['amount'].sum()
        plt.pie(category_expenses, labels=category_expenses.index, autopct='%1.1f%%')
        st.pyplot()

# Closing the database connection
conn.close()
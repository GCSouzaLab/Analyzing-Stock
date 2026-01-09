import streamlit as st

def welcome():
    st.title("Welcome to Stock Analyzer, by Gabriel Cardoso de Souza")
    st.divider()

def about():
    st.subheader("About:")
    st.write("My name is Gabriel, I've done an exchange program in computer science at Universitè Grenoble Alpes,"
             "it's to complement my bachelor."
             "I'm doing it to practice and learn more how programming in Python, "
             "then I got an area I already like to apply some knowledge"
             "The focus of this project is learning python and reinforce how the stock's market works."
    )

if __name__  == "__main__":
    welcome()
    about()
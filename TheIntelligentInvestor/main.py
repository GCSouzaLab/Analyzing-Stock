import streamlit as st

def main():
    pg = st.navigation([
        st.Page(page="pages/welcome.py",title="Welcome investor!", default=True),
        st.Page(page="pages/analyser.py",title="The IntelligentInvestor", url_path="Analysing"),
    ], expanded=True, position="top")
    pg.run()

if __name__  == "__main__":
    main()

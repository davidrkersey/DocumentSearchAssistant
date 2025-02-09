import streamlit as st
import tempfile
from utils.pdf_handler import extract_pdf_text
from utils.text_processor import normalize_text, search_terms, generate_summary
from utils.export_handler import create_excel_export
import pandas as pd

def main():
    st.set_page_config(page_title="Document Search & Analysis", layout="wide")
    
    st.title("Document Search & Analysis Tool")
    st.write("Upload documents and search for specific terms with context.")

    # File upload section
    uploaded_files = st.file_uploader(
        "Upload PDF documents", 
        type=['pdf'], 
        accept_multiple_files=True
    )

    # Search terms input
    search_terms_input = st.text_area(
        "Enter search terms (one per line)",
        height=100,
        help="Enter each search term on a new line"
    )

    if uploaded_files and search_terms_input:
        search_terms_list = [term.strip() for term in search_terms_input.split('\n') if term.strip()]
        
        if st.button("Analyze Documents"):
            with st.spinner("Processing documents..."):
                # Process each document
                all_results = []
                
                for uploaded_file in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        
                        # Extract text from PDF
                        text_by_page = extract_pdf_text(tmp_file.name)
                        
                        # Search for terms
                        for term in search_terms_list:
                            results = search_terms(text_by_page, term)
                            if results:
                                for page_num, excerpts in results.items():
                                    for excerpt in excerpts:
                                        context_summary = generate_summary(excerpt)
                                        all_results.append({
                                            'Document': uploaded_file.name,
                                            'Search Term': term,
                                            'Page': page_num + 1,
                                            'Excerpt': excerpt,
                                            'Summary': context_summary
                                        })

                if all_results:
                    # Display results
                    df = pd.DataFrame(all_results)
                    
                    # Group results by search term for display
                    for term in search_terms_list:
                        term_results = df[df['Search Term'] == term]
                        if not term_results.empty:
                            st.subheader(f"Results for: {term}")
                            for _, row in term_results.iterrows():
                                with st.expander(f"Page {row['Page']} - {row['Document']}"):
                                    st.write("**Excerpt:**")
                                    st.write(row['Excerpt'])
                                    st.write("**Context Summary:**")
                                    st.write(row['Summary'])
                    
                    # Export to Excel
                    excel_file = create_excel_export(df)
                    st.download_button(
                        label="Download Results as Excel",
                        data=excel_file,
                        file_name="search_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No matches found for the provided search terms.")

if __name__ == "__main__":
    main()

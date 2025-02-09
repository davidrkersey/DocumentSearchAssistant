import os
import streamlit as st
import tempfile
from utils.document_handler import create_document_handler
from utils.text_processor import normalize_text, search_terms, generate_summary
from utils.export_handler import create_excel_export
from utils.database import get_db, Document, SearchResult
import pandas as pd
from datetime import datetime

def get_or_create_document(db, filename, page_count):
    """Get existing document or create new one"""
    doc = db.query(Document).filter(Document.filename == filename).first()
    if not doc:
        doc = Document(filename=filename, page_count=page_count)
        db.add(doc)
        db.commit()
        db.refresh(doc)
    return doc

def main():
    st.set_page_config(page_title="Document Search & Analysis", layout="wide")

    st.title("Document Search & Analysis Tool")
    st.write("Upload documents and search for specific terms with context.")

    # Initialize database session
    db = next(get_db())

    # File upload section
    uploaded_files = st.file_uploader(
        "Upload documents (PDF, Word, or Text)", 
        type=['pdf', 'docx', 'doc', 'txt'], 
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
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.read())

                        try:
                            # Create appropriate document handler
                            doc_handler = create_document_handler(tmp_file.name)

                            # Extract text from document
                            text_by_page = doc_handler.extract_text()

                            # Create or get document record
                            doc = get_or_create_document(db, uploaded_file.name, len(text_by_page))

                            # Search for terms
                            for term in search_terms_list:
                                results = search_terms(text_by_page, term)
                                if results:
                                    for page_num, excerpts in results.items():
                                        for excerpt in excerpts:
                                            context_summary = generate_summary(excerpt)

                                            # Store in database
                                            search_result = SearchResult(
                                                document_id=doc.id,
                                                search_term=term,
                                                page_number=page_num + 1,
                                                excerpt=excerpt,
                                                summary=context_summary
                                            )
                                            db.add(search_result)

                                            all_results.append({
                                                'Document': uploaded_file.name,
                                                'Search Term': term,
                                                'Page': page_num + 1,
                                                'Excerpt': excerpt,
                                                'Summary': context_summary
                                            })

                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                            continue

                db.commit()

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

    # Show previous searches
    with st.expander("View Previous Search Results"):
        previous_results = (
            db.query(SearchResult)
            .join(Document)
            .order_by(SearchResult.id.desc())
            .limit(50)
            .all()
        )

        if previous_results:
            for result in previous_results:
                st.write(f"**Document:** {result.document.filename}")
                st.write(f"**Search Term:** {result.search_term}")
                st.write(f"**Page:** {result.page_number}")
                st.write(f"**Excerpt:**\n{result.excerpt}")
                st.write("---")
        else:
            st.write("No previous search results found.")

if __name__ == "__main__":
    main()
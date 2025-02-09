import pandas as pd
import io

def create_excel_export(df):
    """Create Excel file from search results"""
    # Select only required columns for export
    export_df = df[['Search Term', 'Page', 'Excerpt']]
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Search Results')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Search Results']
        for idx, col in enumerate(export_df.columns):
            max_length = max(
                export_df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    output.seek(0)
    return output.getvalue()

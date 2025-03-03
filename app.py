import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager
from query_processor import QueryProcessor
import pandas as pd
from datetime import datetime, timedelta

def create_visualization(df, question):
    """Create appropriate visualization based on the data and question"""
    try:
        
        if df.empty:
            st.warning("No data available for the selected time period.")
            return None

        if any(word in question.lower() for word in ['trend', 'over time', 'monthly', 'daily', 'last 6 months']):
            date_col = df.columns[0]
            value_col = df.columns[1]
            
            fig = px.line(
                df,
                x=date_col,
                y=value_col,
                title='Trend Analysis',
                labels={
                    date_col: date_col.replace('_', ' ').title(),
                    value_col: value_col.replace('_', ' ').title()
                }
            )
            
            fig.update_layout(
                xaxis=dict(
                    title=date_col.replace('_', ' ').title(),
                    tickformat='%Y-%m-%d',
                    tickangle=45
                ),
                yaxis=dict(
                    title=value_col.replace('_', ' ').title()
                ),
                hovermode='x unified'
            )
            
            return fig
            
        elif any(word in question.lower() for word in ['how many', 'count', 'number of customers', 'new customers']):
            value = df.iloc[0, 0]  
            
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="number",
                value=value,
                title={"text": "New Customers"},
                number={"font": {"size": 80}},
                domain={'row': 0, 'column': 0}
            ))
            
            fig.update_layout(
                title="New Customer Count",
                height=400,
                font=dict(size=20)
            )
            
            return fig
            
        elif any(word in question.lower() for word in ['category', 'compare', 'distribution']):
            if len(df.columns) >= 2:
                cat_col = df.columns[0]
                num_col = df.columns[1]
                fig = px.bar(df, x=cat_col, y=num_col,
                            title='Category Comparison',
                            labels={
                                num_col: num_col.replace('_', ' ').title(),
                                cat_col: cat_col.replace('_', ' ').title()
                            })
                
        elif any(word in question.lower() for word in ['top', 'best', 'highest']):
            if len(df.columns) >= 2:
                fig = px.bar(df,
                            x=df.columns[0],
                            y=df.columns[1],
                            title='Top Performance Analysis')
                fig.update_traces(marker_color='rgb(26, 118, 255)')
                
        elif any(word in question.lower() for word in ['share', 'percentage', 'proportion']):
            if len(df.columns) >= 2:
                fig = px.pie(df,
                            values=df.columns[1],
                            names=df.columns[0],
                            title='Distribution Analysis')
                
        else:
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                fig = px.bar(df, y=numeric_cols[0],
                            title='Data Analysis',
                            labels={numeric_cols[0]: numeric_cols[0].replace('_', ' ').title()})
            else:
                fig = px.bar(df, title='Data Analysis')

        fig.update_layout(
            template='plotly_white',
            xaxis_title_standoff=25,
            yaxis_title_standoff=25,
            margin=dict(t=50, l=50, r=50, b=50)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Visualization error: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Arthtattva AI Business Query System", layout="wide")
    
    st.title("Arthtattva AI Business Query System")
    st.write("Ask questions about your business data in natural language and get insights instantly with Arthtattva!")

    st.sidebar.header("Example Questions")
    example_questions = [
        "What was the revenue trend in the last 6 months?",
        "How many new customers did we get last quarter?",
        "What are our top 5 selling products by revenue?",
        "Show me the sales distribution by product category",
        "What's the average transaction value by product category?",
        "Which day of the week has the highest sales?",
        "Show me the monthly customer acquisition trend",
        "What's the revenue share of each product category?",
        "Who are our top 10 customers by purchase value?",
        "What's the daily sales trend during holiday season?"
    ]
    
    for q in example_questions:
        if st.sidebar.button(q):
            st.session_state['question'] = q

    st.sidebar.header("Available Data")
    st.sidebar.markdown("""
    - Customer information
    - Product catalog with categories
    - Sales transactions
    - One year of historical data
    - Holiday season patterns
    """)

    db_manager = DatabaseManager()
    query_processor = QueryProcessor()

    question = st.text_input("💭 Enter your business question:", 
                            key='question',
                            help="Try one of the example questions from the sidebar!")

    if question:
        try:
            with st.spinner("🔄 Processing your question..."):

                sql_query = query_processor.natural_language_to_sql(question)
                
                with st.expander("🔍 View SQL Query"):
                    st.code(sql_query, language='sql')
                
                results = db_manager.execute_query(sql_query)

                st.subheader("📊 Results")
                st.dataframe(results, use_container_width=True)

                fig = create_visualization(results, question)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                with st.expander("📈 Additional Insights"):
                    st.write("Data Summary:")
                    st.write(results.describe())

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

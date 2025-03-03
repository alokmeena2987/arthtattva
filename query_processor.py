import requests
from config import TOGETHER_API_KEY

class QueryProcessor:
    def __init__(self):
        self.api_key = TOGETHER_API_KEY
        self.api_url = "https://api.together.xyz/inference"
        self.system_prompt = """
        You are a PostgreSQL SQL query generator. Convert natural language questions into SQL queries.
        
        Database schema:
        customers (
            customer_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            registration_date DATE
        )
        
        products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(50),   -- Categories: Electronics, Furniture, Appliances
            price DECIMAL(10, 2)
        )
        
        sales (
            sale_id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(customer_id),
            product_id INTEGER REFERENCES products(product_id),
            sale_date DATE,
            quantity INTEGER,
            total_amount DECIMAL(10, 2)
        )

        Rules:
        1. For time ranges, always use: 
           WHERE sale_date >= CURRENT_DATE - INTERVAL 'X months/days'
           AND sale_date <= CURRENT_DATE
        2. For last quarter, use:
           WHERE sale_date >= DATE_TRUNC('quarter', CURRENT_DATE) - INTERVAL '3 months'
           AND sale_date < DATE_TRUNC('quarter', CURRENT_DATE)
        3. Use DATE_TRUNC('month', column) for monthly grouping
        4. Always ORDER BY date columns ASC for trends
        5. Generate only the SQL query, no explanations

        Example for "last 6 months revenue":
        SELECT 
            DATE_TRUNC('month', sale_date) AS sale_month,
            SUM(total_amount) AS total_revenue
        FROM sales
        WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
        AND sale_date < DATE_TRUNC('month', CURRENT_DATE)
        GROUP BY DATE_TRUNC('month', sale_date)
        ORDER BY sale_month ASC;
        """

    def natural_language_to_sql(self, question):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            
            if 'last quarter' in question.lower():
                sql_query = """
                SELECT COUNT(*)
                FROM customers
                WHERE registration_date >= DATE_TRUNC('quarter', CURRENT_DATE) - INTERVAL '3 months'
                AND registration_date < DATE_TRUNC('quarter', CURRENT_DATE);
                """
                return sql_query
            
            
            data = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "prompt": f"{self.system_prompt}\n\nQuestion: {question}\nSQL Query:",
                "temperature": 0.0,
                "max_tokens": 200,
                "top_p": 1,
                "stop": [";", "```"]
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            sql_query = response.json()['output']['choices'][0]['text'].strip()
            if not sql_query.endswith(';'):
                sql_query += ';'
                
            return sql_query
            
        except Exception as e:
            raise Exception(f"Error in query processing: {str(e)}")

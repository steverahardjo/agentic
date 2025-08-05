from converse import Context
import matplotlib.pyplot as plt
from datetime import datetime


class Extension:
    def __init__(self,  request: Context, start_date:datetime, end_date:datetime):
        self.start=start_date
        self.end= end_date
        if request == Context.C:
            return self.calculation()
        elif request == Context.V:
            return self.viz()
    
    def retrieve_db(self, start_date:datetime, end_date:datetime):
        # Convert start_date to string in the format that your database expects (e.g., 'YYYY-MM-DD')
        start_date_str = start_date.strftime('%Y-%m-%d')
        query = "SELECT * FROM your_table WHERE date >= ?"
        self.cursor.execute(query, (start_date_str,))
        results = self.cursor.fetchall()
        return results

    
    def viz(self):
        
        
    def calculation(self): 
        return
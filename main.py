from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import mysql.connector

#class definitions
class LifeEvent(BaseModel):
    life_id: Optional[int] = None
    title: str
    date: Optional[str] = None
    time: Optional[str] = None
    time_till: Optional[str] = None
    color: int

app = FastAPI()

# GET REQUESTS

@app.get("/")              #when the root is visited it calls read root
def read_root():
    return {"message": "API up and running"}


@app.get("/lifes")
def get_all_lifes():
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host="localhost",
            user="zimmerl",
            password="2112",
            database="db_microservice"
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Get all lifes
        cursor.execute("SELECT * FROM lifes")
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"count": len(results), "data": results}
    
    except Exception:
        return {"error with getting lifes"}
    


# POST REQUESTS

@app.post("/lifes")
def create_life_event(event: LifeEvent):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="zimmerl",
            password="2112",
            database="db_microservice"
        )
        
        cursor = connection.cursor()
        
        # INSERT new data
        cursor.execute("INSERT INTO lifes (title, date, time, time_till, color)VALUES (%s, %s, %s, %s, %s)",
                      (event.title, event.date, event.time, event.time_till, event.color))
        
        # Save the changes
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return {"message": "Life event created!"}

    except Exception:
        return {"error with creating new life"}
    


# DELETE REQUESTS
@app.delete("/lifes/{life_id}")
def delete_life_event(life_id: int):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="zimmerl",
            password="2112",
            database="db_microservice"
        )
        
        cursor = connection.cursor()
        
        # Delete the life event
        cursor.execute("DELETE FROM lifes WHERE life_id = %s", (life_id,))
        
        # Check if anything was deleted
        if cursor.rowcount == 0:
            connection.close()
            return {"error": "Life event not found"}
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {"message": "Life event deleted successfully!"}
    
    except Exception:
        return {"error"}
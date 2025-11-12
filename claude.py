from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import mysql.connector
from mysql.connector import pooling
from datetime import date

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "zimmerl",
    "password": "password123",  # Replace with your actual password
    "database": "db_microservice",
    "pool_name": "mypool",
    "pool_size": 5
}

# API Keys for your 5 programs
API_KEYS = {
    "app1-secret-key": "app1",
    "app2-secret-key": "app2",
    "app3-secret-key": "app3",
    "app4-secret-key": "app4",
    "app5-secret-key": "app5"
}

app = FastAPI()

# Connection pool
connection_pool = None

# Data model for creating/updating life events
class LifeEvent(BaseModel):
    title: str
    date: Optional[str] = None  # Format: YYYY-MM-DD
    time: Optional[str] = None
    time_till: Optional[str] = None
    color: Optional[int] = None

# Authentication
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[x_api_key]

# Database connection
def get_db_connection():
    global connection_pool
    if connection_pool is None:
        connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
    return connection_pool.get_connection()

# Health check
@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

# CREATE - Add a new life event
@app.post("/lifes")
def create_life_event(event: LifeEvent, app_name: str = Depends(verify_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            INSERT INTO lifes (title, date, time, time_till, color)
            VALUES (%s, %s, %s, %s, %s)
        """, (event.title, event.date, event.time, event.time_till, event.color))
        
        conn.commit()
        life_id = cursor.lastrowid
        
        # Return the created event
        cursor.execute("SELECT * FROM lifes WHERE life_id = %s", (life_id,))
        result = cursor.fetchone()
        
        return {"message": "Life event created", "data": result}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# READ - Get all life events
@app.get("/lifes")
def get_all_life_events(app_name: str = Depends(verify_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM lifes ORDER BY date DESC")
        results = cursor.fetchall()
        return {"count": len(results), "data": results}
    finally:
        cursor.close()
        conn.close()

# READ - Get a specific life event by ID
@app.get("/lifes/{life_id}")
def get_life_event(life_id: int, app_name: str = Depends(verify_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM lifes WHERE life_id = %s", (life_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Life event not found")
        
        return {"data": result}
    finally:
        cursor.close()
        conn.close()

# UPDATE - Update a life event
@app.put("/lifes/{life_id}")
def update_life_event(life_id: int, event: LifeEvent, app_name: str = Depends(verify_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            UPDATE lifes 
            SET title = %s, date = %s, time = %s, time_till = %s, color = %s
            WHERE life_id = %s
        """, (event.title, event.date, event.time, event.time_till, event.color, life_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Life event not found")
        
        conn.commit()
        
        cursor.execute("SELECT * FROM lifes WHERE life_id = %s", (life_id,))
        result = cursor.fetchone()
        
        return {"message": "Life event updated", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# DELETE - Delete a life event
@app.delete("/lifes/{life_id}")
def delete_life_event(life_id: int, app_name: str = Depends(verify_api_key)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM lifes WHERE life_id = %s", (life_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Life event not found")
        
        conn.commit()
        return {"message": "Life event deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
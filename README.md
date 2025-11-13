**--Intro--**<br>
This microservice is a database system coupled with a python API that allows for CREATE, READ, and DELETE functionality. It is hosted via MariaDB and accessed with localhost at the address http://127.0.0.1:8000/. Currently it only works for programs on the same computer because it is a localhost, but it is still a microservice with everything transferred by HTTP. It can also be easily modified to have online hosting, but that costs money so currently its not a feature.

**A. Instructions for how to REQUEST data from the database.**<br>
To request data from the database, you must first write an SQL query that will retrieve all the data within the database.

The example call for the test program is: SELECT * FROM lifes

This selects all the data in the lifes table. Once you have made your SQL query, we will add a GET request method to the API with your query which will inject this query into the database.

To request data from the database within your program, initiate an HTTP GET request to the address http://127.0.0.1:8000/your_program<br>
In the example program, this looks like this: requests.get("http://127.0.0.1:8000/lifes")

This calls the GET method within the API and queries the database for your requested data

-- Full example call --<br>
HTTP GET request within the test program: requests.get("http://127.0.0.1:8000/lifes")<br>
SQL query within the API: cursor.execute("SELECT * FROM lifes")<br>
                            results = cursor.fetchall()
    
    

**B. Instructions for how to RECEIVE data from the database.**<br>
When you have done the steps above to REQUEST data, to RECIEVE data from the database, you must add a variable to collect the HTTP response.<br>
The API returns your get request as a JSON with the line: return {"count": len(results), "data": results}

In your program set a variable equal to the get request like this:<br>
response = requests.get("http://127.0.0.1:8000/your_program")

Now your variable holds the json response data and you can parse the values into your program.

This process will vary depending on the language and libraries you use, but here's an example call with the test program in python:

-- Full example call --<br>
JSON data returned by the API: return {"count": len(results), "data": results}<br>
<br>
In the test program:<br>
response = requests.get("http://127.0.0.1:8000/lifes")<br>
    if response.status_code == 200:<br>
        data = response.json()<br>
<br>
for life in data['data']:<br>
    life_id = life['life_id']<br>
    title = life['title']<br>
    date = life.get('date', '')<br>
    time = life.get('time', '')<br>
    time_till = life.get('time_till', '')<br>
    color_num = life.get('color', 1)<br>
<br>

**C. UML sequence diagram showing how requesting and receiving data works**<br>
![alt text](https://github.com/zimmerl99/database_microservice361/blob/main/UML%20Sequence%20Diagram.png?raw=true)

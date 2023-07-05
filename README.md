# Documentation:

## What went well:

    1. Getting the data:
        - The GraphQL query was quite easy to create. It is a very simple query that filters data based on token address between two timestamps
        - The end timestamp would always be the current datetime no matter what
        - The start timestamp would either be 7 days before the current datetime if there were no records present or it would be the datetime + 1 hour of the latest record
        - This way we always have the most up to date data
        - I also rounded the timestamps to the nearest hour so we can store clean hourly data
        Task Scheduler:
            - Since one of the requirements was to have a single point of entry to start up an API service and an ingestion service I decided to use a task scheduler that would go off every hour to ingest data while the API was still running. The task scheduler was implemented from the apscheduler library and upon start of the flask app it will run on a separate thread. I also don't need to worry about any concurrent calls on the database. By default, PostgreSQL uses a multiversion concurrency control (MVCC) mechanism, which allows for concurrent reads and writes without blocking each other. Readers will not block writers, and writers will not block readers. This means that you can perform read operations (e.g., SELECT queries) on the database while the scheduler is writing data without any immediate conflicts.
    
    2. Ingesting/Storing the data:
        - The database models I decided to use are also quite simple
        - There are two simple tables. One that stores the hourly data we want to serve in the API and the other that stores the latest token metadata
        - We can filter data in the hourly table by using the token_address and date field

    3. Serving the data:
        - I decided to use Flask for the API to serve our data
        - Querying the data from our database was as simple as using sql alchemy calls. To get the data in an interval format sqlalchemy has a built in generate_series function that will filter data in an interval

## What could have gone better:
    1. I have mentioned a couple of TODO's in the comments of my code that I would like to have gone better
    2. I didn't set the app up properly in the beginning to segment my code out in multiple classes. I think I needed to use the sql alchemy engine class and some others if I wanted to keep my models in a separate class. Because of this the only way to make my tables was to copy the models into my main class and run it there.

## Is there anything specific you'd like to come back and improve if you had time? Why?
    1. It would have been nice to do some more research on the libraries and frameworks i'm using. If we wanted to productionalize this system we would have needed to do a lot more research into the task scheduling library to make sure its the most memory and time efficient library in python. Also, it would be nice to see the difference between Flask and other python API frameworks like Django. 
    2. It also would have been good to add more error handling within the code. At the moment there is very limited error handling within the database calls and API calls
    3. I would definitley like to add some automated unit and integration tests in here. I've done some extensive testing by myself but it would be better to put that in some code so we can run it pre deployments
    4. There were also a lot of TODO's in the code that would have been nice to fix / optimize
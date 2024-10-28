The application can be build/launched easlily with `docker compose -f docker-compose-app.yml up1` (just a single command). Below screenshots are provided tp give end-users and testers an idea of what to expect.


## Building/Running the Application

On running the builds command for the first time, it will download everything so terminal messages as in below screenshots will be observed:
-- yet to upload

Upon running the command `docker compose -f docker-compose-app.yml up1` (or maybe you have used docker-compose instead) terminal will look more or less like this:
![scrshot_terminal1](https://github.com/user-attachments/assets/25de84ea-1cf2-44b6-b1a4-da7bb1ec62c9)

It can be seen in above image that database was already initiated so it is now being skipped. Similarly, ollama model will be downloaded on the first run and afterwards below logs will be seen:
![scrshot_terminal2](https://github.com/user-attachments/assets/31aafa78-1741-4145-95cf-492666ddbb38)

Once ElasticSearch and postgreSQL containers are created it will trigger streamlit service. This also kicks off entrypoint bash script which starts prefect server and streamlit UI. Below log entries will be observed:
![scrshot_terminal3](https://github.com/user-attachments/assets/d69277d3-1db6-4a65-8852-12795cfd9bfb)

![scrshot_terminal4](https://github.com/user-attachments/assets/a622dd6a-da4b-4f6a-9427-4db36b85448c)



## Streamlit UI

Streamlit Home Page will take 5-10 seconds to load once you open the url http://localhost:8501/. After this, it will show initialization status as shown below:
-- yet to upload

UI Initialization takes <1 minute and then you can jump to 'AI Assistant' page because initialization will index around 10 videos to be used immediately. Below is one example usage:
![scrshot_ai_assistant](https://github.com/user-attachments/assets/fe4a2fad-a9a1-4cf7-baec-7de2855ccb9b)

The above screenshot does not show feedback option which was added later on, below screenshot shows the same page with feedback option implemented:
![scrshot_ai_assistant_feedback](https://github.com/user-attachments/assets/055def09-a914-4aa5-b9f6-97d94954a02b)

Go to the 'Add Video' tab to add any new videos to interact with. This takes time so try adding short videos of length 10-15 minutes if you're just testing. Below screenshot shows how it looks:
-- yet to upload



## Prefect Data Orchestration

Adding/Indexing new videos in the application will trigger data ingest pipeline which can be viewed in prefect ui interface by going to url http://localhost:4200/
![scrshot_prefect](https://github.com/user-attachments/assets/1838bf8b-a2cb-4a6d-8f91-1506ce50c952)



## Viewing the postgreSQL database

Go to url http://localhost:8080/ to access Adminer with credentials provided in readme. Below screenshots show the two tables for user conversations and feedbacks:
![scrshot_adminer_conversation](https://github.com/user-attachments/assets/74693b4a-41b1-470f-a715-1f03d96a8dd3)

![scrshot_adminer_feedback](https://github.com/user-attachments/assets/e59fc49f-7c53-46e1-81b6-16ea6d85ba31)


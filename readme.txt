The package contains a docker container that runs the application via localhost using port 5000. 
The container does all necessary Python version and package installations. The application 
may also be viewed at https://gatech-2024-6242-85.azurewebsites.net/. The instructions to spin
up the web app in Azure are below. 

Docker Build: 
1. Install Docker (https://www.docker.com/products/docker-desktop/) and ensure the daemon is 
running (just opening the desktop application is sufficient).
2. In a terminal, run the following two lines:
    docker build -t ev_station_prediction .
    docker run -p 5000:5000 ev_station_prediction
3. Search for localhost in a web browser and interact with the app.

Azure Webapp Build: 
Run the following lines:
    az webapp up --name gatech-2024-6242-85 --resource-group 6242
    az webapp config appsettings set --name gatech-2024-6242-85 --resource-group 6242 --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
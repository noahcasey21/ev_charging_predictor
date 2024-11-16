docker build -t ev_station_prediction .
docker run -p 5000:5000 ev_station_prediction
az webapp up --name gatech-2024-6242-85 --resource-group 6242
az webapp config appsettings set --name gatech-2024-6242-85 --resource-group 6242 --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
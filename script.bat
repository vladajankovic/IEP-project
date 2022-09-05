docker build -t authapplication --file .\authApplication.dockerfile .
docker build -t authdbmigration --file .\authDBMigration.dockerfile .
docker build -t warehouse --file .\warehouse.dockerfile .
docker build -t daemon --file .\daemon.dockerfile .
docker build -t storedbmigration --file .\storeDBMigration.dockerfile .
docker build -t buyer --file .\buyer.dockerfile .
docker build -t admin --file .\admin.dockerfile .
docker swarm init
docker stack deploy --compose-file .\stack.yaml iep

# Mobile.de
Neural network trained on data from mobile.de for a university project

## Docker
You can use docker to build and run the webserver part of the project.
To build the image, run the following command from the project root folder:
```shell
docker build -t mobile.ai -f .\webinterface\dockerfile .
```
To run the container, run the following command:
```shell
docker run -p 5000:5000 mobile.ai
```
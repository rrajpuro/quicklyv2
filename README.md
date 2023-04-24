# Quicklyv2
## Quickly CDN Service Readme

Quickly is a Content Delivery Network (CDN) service that deploys infrastructure on a Linux machine and provides tenant isolation. This readme is intended for service providers who will be using the service internally and need to understand its internal workings.

## Requirements

To use Quickly, you will need a Linux machine with the following software installed:

- Docker (version 19.03 or later)
- Docker Compose (version 1.25 or later)
- Git

## Installation

1. Clone the Quickly repository onto your Linux machine:

git clone https://github.com/quickly/cdn-service.git


2. Navigate to the `cdn-service` directory:

cd cdn-service


3. Run the installation script:

./install.sh


The installation script will download and install all necessary dependencies, including Docker and Docker Compose.

## Configuration

Before running the Quickly service, you will need to configure it by setting some environment variables. You can set these variables either directly in the terminal or by creating a `.env` file in the `cdn-service` directory.

The following variables are required:

- `QUICKLY_API_KEY`: Your API key for the Quickly service.
- `QUICKLY_DB_PASSWORD`: A strong password for the Quickly service's database.

The following variables are optional:

- `QUICKLY_PORT`: The port number on which to run the Quickly service. Defaults to `8080`.
- `QUICKLY_DB_NAME`: The name of the Quickly service's database. Defaults to `quickly`.
- `QUICKLY_DB_USER`: The username for the Quickly service's database. Defaults to `quickly`.
- `QUICKLY_DB_HOST`: The hostname for the Quickly service's database. Defaults to `db`.

## Usage

To start the Quickly service, run the following command:

docker-compose up -d


This will start the Quickly service in the background. You can then access the service by visiting `http://<your-server>:<QUICKLY_PORT>/` in your web browser.

To stop the Quickly service, run the following command:

docker-compose down


## Maintenance

To update the Quickly service to the latest version, run the following commands:

git pull
docker-compose down
docker-compose up -d


This will download and install the latest version of the Quickly service and start it in the background.

## Troubleshooting

If you encounter any issues with the Quickly service, you can view the service's logs by running the following command:

docker-compose logs -f


This will show the logs for all containers in the Quickly service. If you need to view the logs for a specific container, you can specify the container name by running the following command:

docker-compose logs -f <container-name>


Replace `<container-name>` with the name of the container whose logs you want to view.

## Conclusion

Thank you for choosing the Quickly CDN service. If you have any questions or issues, please contact our support team at support@quicklycdn.com.


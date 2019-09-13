# Preprocessing Service
This service is responsible doing the preprocessing of the publishers streams.
It takes one publisher stream as source, and generate the events with each frame into our system, based on a specific FPS and resolution.

# Commands Stream
## Inputs

### startPreprocessing
```json
{
    "action": "startPreprocessing",
    "publisher_id": "44d7985a-e41e-4d02-a772-a8f7c1c69124",
    "source": "rtmp://localhost/live/mystream",
    "resolution": "640x480",
    "fps": "30",
    "buffer_stream_key": "buffer-stream-key"
}
```

### stopPreprocessing
```json
{
    "action": "stopPreprocessing",
    "buffer_stream_key": "buffer-stream-key"
}
```
## Outputs
None

# Data Stream
Generate event data with the following fields, as the following example:
```json
{
    "id": "publisher-id-2-6c80a860-6a08-4d22-a9b9-9acf7016b863",
    "publisher_id": "publisher-id-2",
    "source": "rtmp://172.17.0.1/live/mystream",
    "image_url": "c8d025d3-8c3a-460c-a6f5-cabb7b179807",
    "vekg": {},
    "width": 640,
    "height": 480,
    "color_channels": "BGR"
}
```

# Installation

## Configure .env
Copy the `example.env` file to `.env`, and inside it replace `SIT_PYPI_USER` and `SIT_PYPI_PASS` with the correct information.

## Installing Dependencies

### Using pipenv
Run `$ pipenv shell` to create a python virtualenv and load the .env into the environment variables in the shell.

Then run: `$ pipenv install` to install all packages, or `$ pipenv install -d` to also install the packages that help during development, eg: ipython.
This runs the installation using **pip** under the hood, but also handle the cross dependency issues between packages and checks the packages MD5s for security mesure.


### Using pip
To install using pip directly, one needs to use the `--extra-index-url` when running the `pip install` command, in order for to be able to use our private Pypi repository.

Load the environment variables from `.env` file using `source load_env.sh`.

To install from the `requirements.txt` file, run the following command:
```
$ pip install --extra-index-url https://${SIT_PYPI_USER}:${SIT_PYPI_PASS}@sit-pypi.herokuapp.com/simple -r requirements.txt
```

# Running
Inside the python environment (virtualenv or conda environment), run:
```
$ ./preprocessing/.run.py
```

# Testing
Run the script `run_tests.sh`, it will run all tests defined in the **tests** directory.

Also, there's a python script at `./preprocessing/send_msgs_test.py` to do some simple manual testing, by sending msgs to the service stream key.


# Docker
## Build
Build the docker image using: `docker-compose build`

**ps**: It's required to have the .env variables loaded into the shell so that the container can build properly. An easy way of doing this is using `pipenv shell` to start the python environment with the `.env` file loaded or using the `source load_env.sh` command inside your preferable python environment (eg: conda).

## Run
Use `docker-compose run --rm service` to run the docker image


# Docker base image.
FROM python:3.9

# Working directory inside the container.
WORKDIR /code

# Copy the requirements.txt inside the image.
COPY ./requirements.txt /code/requirements.txt

# Install project dependencies.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy project files to the image.
COPY ./app /code/app

# Run the contianer - force port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Ensure the virtual environment is activated when running Django commands
ENV PATH="/opt/venv/bin:$PATH"

# Run Django migrations and collect static files
RUN python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Command to run the Django app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stud_test.wsgi:application"]

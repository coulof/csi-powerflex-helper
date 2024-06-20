FROM python:3.12

# Install Ansible

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

RUN ansible-galaxy collection install dellemc.powerflex

# Copy the application code
COPY . .

EXPOSE 5000

# Set the environment variable
ENV FLASK_APP app.py

# Set the entrypoint to start the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

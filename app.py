from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file
import threading
import subprocess
import yaml

app = Flask(__name__)
jobs = {}

# Define a function to launch the Ansible job
def launch_ansible_job(endpoint, user, password):
    #command = f"ansible-playbook -i /path/to/hosts -l {endpoint} -u {user} -p {password} playbook.yml"
    print("Job launched for: ", endpoint)
    command = f"ansible-playbook playbooks/gather-facts-and-generate-config.yaml -e 'gateway_host={endpoint} port=443 username={user} password={password}'"
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(process.stdout)
        jobs[endpoint]= {'name': endpoint, 'status': 'finished!', 'output': process.stdout, 'file': f"config-{endpoint}.zip"}
    except subprocess.CalledProcessError:
        jobs[endpoint]= {'name': endpoint, 'status': 'failed!', 'output': process.stdout}

@app.route('/job/<endpoint>')
def job_details(endpoint):
    if endpoint in jobs:
        return render_template('job.html', job=jobs[endpoint])
    else:
        return jsonify({'message': 'Job not found'}), 404

@app.route('/download/<endpoint>', methods=['GET'])
def download_file(endpoint):
    print(jobs)
    print('debuf')
    print(endpoint)
    return send_file(f"playbooks/{jobs[endpoint]['file']}", as_attachment=True)

# Define a route for the form submission
@app.route('/submit', methods=['POST'])
def submit_form():
    endpoint = request.form['endpoint']
    user = request.form['username']
    password = request.form['password']
    jobs[endpoint]= {'name': endpoint, 'status': 'launched!', 'output': ''}

    # Launch the Ansible job
    threading.Thread(target=launch_ansible_job, args=(endpoint, user, password)).start()
    #return jsonify({'message': 'Job launched!'}), 200
    return redirect(url_for('form_page'))

# Define a route for the status
@app.route('/status', methods=['GET'])
def status():
    return jsonify(jobs), 200

# Define a route for the form page
@app.route('/')
def form_page():
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)

import os
import shutil
import subprocess
import time
import requests

def get_latest_commit(repo_url):
    api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/commits/main"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        commit_data = response.json()
        return commit_data['sha']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest commit: {e}")
        return None

def backup_application(main_application_path, backup_destination):
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(backup_destination, f"backup_{timestamp}")
    try:
        if os.path.exists(main_application_path):
            print("Backing up application...")
            shutil.copytree(main_application_path, backup_path)
            print(f"Backup completed: {backup_path}")
        else:
            print(f"Main application path does not exist: {main_application_path}")
    except Exception as e:
        print(f"Error during backup: {e}")
        exit(1)

def delete_main_application(main_application_path):
    try:
        if os.path.exists(main_application_path):
            print("Deleting main application...")
            shutil.rmtree(main_application_path)
            print("Main application deleted.")
        else:
            print(f"Main application path does not exist: {main_application_path}")
    except Exception as e:
        print(f"Error during deletion: {e}")
        exit(1)

def clone_repository(repo_url, destination_path):
    try:
        print("Cloning repository...")
        subprocess.run(["git", "clone", repo_url, destination_path], check=True)
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during repository cloning: {e}")
        exit(1)

def reload_services():
    try:
        print("Reloading services...")
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "flask_app"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "nginx"], check=True)
        print("Services reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during service reload: {e}")
        exit(1)

def auto_deploy():
    main_application_path = "/home/ubuntu/p_wise"
    backup_destination = "/home/ubuntu/backup"
    repo_url = "https://github.com/mahpatelx/cloud_project_backend"

    # Step 1: Backup the main application
    backup_application(main_application_path, backup_destination)

    # Step 2: Delete the current main application
    delete_main_application(main_application_path)

    # Step 3: Clone the latest code from the repository
    clone_repository(repo_url, main_application_path)

    # Step 4: Reload services
    reload_services()

def monitor_and_deploy():
    repo_url = "https://github.com/mahpatelx/cloud_project_backend"
    main_application_path = "/home/ubuntu/p_wise"
    backup_destination = "/home/ubuntu/backup"

    print("Starting GitHub monitoring...")
    last_commit = get_latest_commit(repo_url)
    if not last_commit:
        print("Failed to fetch initial commit. Exiting...")
        return

    print(f"Initial commit hash: {last_commit}")
    while True:
        time.sleep(60)  # Check every 60 seconds
        current_commit = get_latest_commit(repo_url)
        if current_commit and current_commit != last_commit:
            print("Change detected in repository. Deploying new changes...")
            auto_deploy()
            last_commit = current_commit
        else:
            print("No changes detected.")

if __name__ == "__main__":
    monitor_and_deploy()

#!/usr/bin/env python3
import os
import sys
import subprocess
import getpass
import secrets
import string
from pathlib import Path

class SetupWizard:
    def __init__(self):
        self.project_dir = Path(__file__).resolve().parent
        self.env_file = self.project_dir / '.env'
        self.venv_dir = self.project_dir / 'venv'
        self.requirements_file = self.project_dir / 'requirements.txt'
        self.pip_path = None
        self.python_path = None

    def print_welcome(self):
        print("\n=== SEO Dashboard Installation Wizard ===")
        print("This wizard will help you set up the SEO Dashboard application.")
        print("Make sure you have Python 3.8+ and pip installed.\n")

    def check_python_version(self):
        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required.")
            sys.exit(1)

    def create_virtual_environment(self):
        print("\nCreating virtual environment...")
        try:
            # Remove existing venv if it exists
            if self.venv_dir.exists():
                print("Removing existing virtual environment...")
                import shutil
                shutil.rmtree(str(self.venv_dir))
            
            # Try creating virtualenv using alternative methods
            methods = [
                # Method 1: Standard venv with system packages
                lambda: subprocess.run([sys.executable, '-m', 'venv', '--system-site-packages', str(self.venv_dir)], check=True),
                # Method 2: Standard venv without system packages
                lambda: subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)], check=True),
                # Method 3: Using virtualenv if available
                lambda: subprocess.run(['virtualenv', str(self.venv_dir)], check=True),
            ]
            
            success = False
            for method in methods:
                try:
                    print("Attempting to create virtual environment...")
                    method()
                    success = True
                    break
                except subprocess.CalledProcessError:
                    continue
                except FileNotFoundError:
                    continue
            
            if not success:
                print("\nAll virtual environment creation methods failed.")
                print("Attempting to install virtualenv...")
                try:
                    # Try to install virtualenv
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'virtualenv'], check=True)
                    subprocess.run(['virtualenv', str(self.venv_dir)], check=True)
                    success = True
                except subprocess.CalledProcessError as e:
                    print(f"Error installing virtualenv: {e}")
                    print("\nPlease try the following steps manually:")
                    print("1. python3 -m pip install --user virtualenv")
                    print("2. python3 -m virtualenv venv")
                    return False
            
            # Set the correct pip and python paths
            if os.name == 'nt':  # Windows
                self.pip_path = self.venv_dir / 'Scripts' / 'pip'
                self.python_path = self.venv_dir / 'Scripts' / 'python'
            else:  # Unix/Linux
                self.pip_path = self.venv_dir / 'bin' / 'pip'
                self.python_path = self.venv_dir / 'bin' / 'python'
            
            # Verify paths exist
            if not self.pip_path.exists():
                raise FileNotFoundError(f"pip not found at {self.pip_path}")
            if not self.python_path.exists():
                raise FileNotFoundError(f"python not found at {self.python_path}")
            
            # Upgrade pip
            print("Upgrading pip...")
            try:
                subprocess.run([str(self.python_path), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
            except subprocess.CalledProcessError:
                print("Warning: Failed to upgrade pip, continuing with installation...")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            print("\nTroubleshooting steps:")
            print("1. Try installing virtualenv:")
            print("   python3 -m pip install --user virtualenv")
            print("2. Create virtual environment manually:")
            print("   python3 -m virtualenv venv")
            print("3. If the above fails, try:")
            print("   sudo apt-get update")
            print("   sudo apt-get install python3-venv python3-dev")
            return False
        except Exception as e:
            print(f"Unexpected error creating virtual environment: {e}")
            print("\nPlease try creating the virtual environment manually:")
            print("python3 -m pip install --user virtualenv")
            print("python3 -m virtualenv venv")
            return False

    def install_requirements(self):
        print("\nInstalling required packages...")
        try:
            # Install wheel first
            subprocess.run([str(self.pip_path), 'install', 'wheel'], check=True)
            
            # Install requirements
            subprocess.run([str(self.pip_path), 'install', '-r', str(self.requirements_file)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error installing requirements: {e}")
            return False

    def generate_secret_key(self):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(50))

    def get_database_credentials(self):
        print("\n=== Database Configuration ===")
        print("Please enter your database credentials:")
        
        db_config = {
            'ENGINE': input("Database engine (1: PostgreSQL, 2: MySQL) [2]: ") or "2",
            'NAME': input("Database name: "),
            'USER': input("Database user: "),
            'PASSWORD': getpass.getpass("Database password: "),
            'HOST': input("Database host [localhost]: ") or "localhost",
            'PORT': input("Database port [3306]: ") or "3306"
        }
        
        # Convert engine choice to actual engine setting
        db_config['ENGINE'] = {
            "1": "django.db.backends.postgresql",
            "2": "django.db.backends.mysql"
        }.get(db_config['ENGINE'], "django.db.backends.mysql")
        
        return db_config

    def create_env_file(self, db_config):
        print("\nCreating environment file...")
        try:
            secret_key = self.generate_secret_key()
            
            env_content = f"""# Django Settings
DJANGO_SETTINGS_MODULE=seo_dashboard.settings
DJANGO_SECRET_KEY='{secret_key}'
DJANGO_DEBUG=False

# Database Settings
DB_ENGINE={db_config['ENGINE']}
DB_NAME={db_config['NAME']}
DB_USER={db_config['USER']}
DB_PASSWORD={db_config['PASSWORD']}
DB_HOST={db_config['HOST']}
DB_PORT={db_config['PORT']}

# Email Settings (configure these later)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Security Settings
ALLOWED_HOSTS=.localhost,127.0.0.1,[your-domain-here]
CSRF_TRUSTED_ORIGINS=https://[your-domain-here]
"""
            
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            return True
        except Exception as e:
            print(f"Error creating .env file: {e}")
            return False

    def setup_database(self):
        print("\nSetting up database...")
        try:
            subprocess.run([str(self.python_path), 'manage.py', 'migrate'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting up database: {e}")
            return False

    def create_superuser(self):
        print("\nCreating superuser account...")
        try:
            subprocess.run([str(self.python_path), 'manage.py', 'createsuperuser'], check=False)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating superuser: {e}")
            return False

    def collect_static(self):
        print("\nCollecting static files...")
        try:
            subprocess.run([str(self.python_path), 'manage.py', 'collectstatic', '--noinput'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error collecting static files: {e}")
            return False

    def setup_permissions(self):
        print("\nSetting up file permissions...")
        try:
            if os.name != 'nt':  # Skip on Windows
                # Create directories if they don't exist
                media_dir = self.project_dir / 'media'
                static_dir = self.project_dir / 'staticfiles'
                media_dir.mkdir(exist_ok=True)
                static_dir.mkdir(exist_ok=True)
                
                # Set permissions
                subprocess.run(['chmod', '-R', '755', str(self.project_dir)], check=True)
                subprocess.run(['chmod', '-R', '775', str(media_dir)], check=True)
                subprocess.run(['chmod', '-R', '775', str(static_dir)], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting permissions: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error setting permissions: {e}")
            return False

    def print_completion(self):
        print("\n=== Installation Complete ===")
        print("The SEO Dashboard has been successfully installed!")
        print("\nNext steps:")
        print("1. Configure your web server (Nginx/Apache)")
        print("2. Set up SSL certificate")
        print("3. Update ALLOWED_HOSTS in .env file")
        print("4. Configure email settings in .env file")
        print("\nTo start the development server:")
        print(f"cd {self.project_dir}")
        print("source venv/bin/activate  # On Unix/Linux")
        print("python manage.py runserver")

    def run(self):
        try:
            self.print_welcome()
            self.check_python_version()
            
            if not self.create_virtual_environment():
                print("Failed to create virtual environment. Installation aborted.")
                sys.exit(1)
            
            if not self.install_requirements():
                print("Failed to install requirements. Installation aborted.")
                sys.exit(1)
            
            db_config = self.get_database_credentials()
            
            if not self.create_env_file(db_config):
                print("Failed to create .env file. Installation aborted.")
                sys.exit(1)
            
            if not self.setup_database():
                print("Failed to set up database. Installation aborted.")
                sys.exit(1)
            
            if not self.create_superuser():
                print("Failed to create superuser. Installation aborted.")
                sys.exit(1)
            
            if not self.collect_static():
                print("Failed to collect static files. Installation aborted.")
                sys.exit(1)
            
            if not self.setup_permissions():
                print("Failed to set permissions. Installation aborted.")
                sys.exit(1)
            
            self.print_completion()
            
        except KeyboardInterrupt:
            print("\nInstallation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error during installation: {e}")
            sys.exit(1)

if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run() 
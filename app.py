import os
import shutil
import subprocess
import time
import logging


class FileEncryptor:
    def __init__(self):
        self.local_dir = 'Local'
        self.encrypt_dir = '1. Encrypt'
        self.vault_dir = '2. Vault'
        self.decrypt_dir = '3. Decrypt'
        self.key_file = 'key.txt'

        self.setup_logging()
        self.create_directories()
        self.generate_key_file()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def create_directories(self):
        directories = [self.local_dir, self.encrypt_dir,
                       self.vault_dir, self.decrypt_dir]
        [os.makedirs(name, exist_ok=True) for name in directories]

    def generate_key_file(self):
        if not os.path.exists(self.key_file):
            try:
                subprocess.run(['age-keygen', '-o', self.key_file], check=True)
                self.logger.info("Key file generated successfully.")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to generate key file: {e}")

    def encrypt_file(self, file_path):
        file_name = os.path.basename(file_path)
        encrypted_file_path = os.path.join(self.vault_dir, f"{file_name}.age")

        try:
            with open(self.key_file, 'r') as key_file:
                private_key = key_file.readlines(
                )[1].partition(':')[-1].strip()

            subprocess.run(['age', '-r', private_key, '-o',
                           encrypted_file_path, file_path], check=True)
            os.remove(file_path)
            self.logger.info(f"Encrypted file '{
                             file_name}' and moved to '{self.vault_dir}'")
            return encrypted_file_path
        except (subprocess.CalledProcessError, IOError) as e:
            self.logger.error(f"Failed to encrypt file '{file_name}': {e}")
            return None

    def decrypt_file(self, file_path):
        file_name = os.path.basename(file_path).replace('.age', '')
        decrypted_file_path = os.path.join(self.local_dir, file_name)

        try:
            subprocess.run(['age', '--decrypt', '-i', self.key_file,
                           '-o', decrypted_file_path, file_path], check=True)
            os.remove(file_path)
            self.logger.info(f"Decrypted file '{
                             str(file_path).partition('/')[-1]}' and moved to '{self.local_dir}'")
            return decrypted_file_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to decrypt file '{file_name}': {e}")
            return None

    def process_files(self, directory, process_function, target_dir):
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                processed_file_path = process_function(file_path)
                if processed_file_path and not os.path.exists(processed_file_path):
                    shutil.move(processed_file_path, target_dir)

    def run(self):
        while True:
            self.process_files(
                self.encrypt_dir, self.encrypt_file, self.vault_dir)
            self.process_files(
                self.decrypt_dir, self.decrypt_file, self.local_dir)
            time.sleep(1)


if __name__ == '__main__':
    file_encryptor = FileEncryptor()
    file_encryptor.run()

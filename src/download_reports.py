try:
    import unzip_requirements
except ImportError:
    pass

from io import BytesIO
from datetime import date
import os
import time
import random

from botocore.exceptions import ClientError
from dotenv import load_dotenv
import boto3
import paramiko
from paramiko.ssh_exception import SSHException

from src.main_db import DBInstance

load_dotenv()


def handler(event, context):
    sftp_file = SFTPFile(account=event["account"], date_file=event["file_date"])
    return {
        'file_name': sftp_file.download_file()
    }


class SFTPFile:
    def __init__(self, account, date_file):
        self.account = account
        self.date_file = date_file
        self.client = boto3.client(
            service_name="s3",
            region_name=os.getenv("REGION"),
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY")
        )

    def download_file(self):
        with BytesIO() as data:
            time.sleep(random.uniform(0.5, 5.5))
            try:
                transport = paramiko.Transport(self.account[1], 22)
                transport.connect(username=self.account[2], password=self.account[3])
            except SSHException as error:
                self.__write_log(message=error, status=0)
            else:
                with paramiko.SFTPClient.from_transport(transport) as sftp:
                    sftp.chdir(path="upload/Report")
                    sftp.getfo(f"{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip", data)
                    data.seek(0)
                    try:
                        self.client.upload_fileobj(
                            data,
                            os.getenv("BUCKET_ZIP_FILES"),
                            f"{self.account[2]}_{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip"
                        )
                    except ClientError as error:
                        self.__write_log(message=error, status=0)
                    else:
                        self.__write_log(message="Download zip file successfully", status=0)
                        return f"{self.account[2]}_{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip"

    def __write_log(self, message, status):
        db = DBInstance(public_key=os.getenv("CLIENT_KEY"))
        if self.account[4]:
            db.handler(query=f"""
                INSERT INTO em_blue_migration_log (date_migrated, account_id, event_migrated, file_name, status, 
                    message, created_at
                )
                VALUES ('{date.today()}', {self.account[0]}, 0, 
                    '{f"{self.account[2]}_{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip"}', {status},
                    '{str(message)}', '{date.today()}');
                """
            )

        if self.account[5]:
            db.handler(query=f"""
                INSERT INTO em_blue_migration_log (date_migrated, account_id, event_migrated, file_name, status, 
                    message, created_at
                )
                VALUES (
                    '{date.today()}', {self.account[0]}, 1,
                    '{f"{self.account[2]}_{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip"}', {status},
                    '{str(message)}', '{date.today()}');
                """
            )

        if self.account[6]:
            db.handler(query=f"""
                INSERT INTO em_blue_migration_log (date_migrated, account_id, event_migrated, file_name, status, 
                    message, created_at
                )
                VALUES (
                    '{date.today()}', {self.account[0]}, 2,
                    '{f"{self.account[2]}_{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip"}', {status},
                    '{str(message)}', '{date.today()}'
                );
                """
            )

        if self.account[7]:
            db.handler(query=f"""
                INSERT INTO em_blue_migration_log (date_migrated, account_id, event_migrated, file_name, status, 
                    message, created_at
                )
                VALUES (
                    '{date.today()}', {self.account[0]}, 3,
                    '{f"{self.account[2]}_{os.getenv('FILE_BASE_NAME')}_{self.date_file}.zip"}', {status},
                    '{str(message)}', '{date.today()}');
                """
                                     )
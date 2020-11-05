"""
upload.py
This file contains functions for uploading to learning platforms
Currently supports: BlackBoard
"""
import subprocess


def upload_to_blackboard(filepath):
    """
    Upload questions to blackboard
    :param filepath: textfile u want to be uploaded
    :return:
    """
    subprocess.run(["text2qti", "--pandoc-mathml", filepath])


if __name__ == '__main__':
    upload_to_blackboard("E1.txt")

    #for i in range(1, 9):
     #   upload_to_blackboard(f"./E{i}.txt")

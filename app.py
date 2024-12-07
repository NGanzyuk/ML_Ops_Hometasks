import subprocess
import os


def run_flask():
    subprocess.Popen(["python", "api/back.py"])


def run_streamlit():
    subprocess.Popen(["streamlit", "run", "api/front.py"])


def run_grpc_service():
    subprocess.Popen(["python", "grpcService/grpc_service.py"])


if __name__ == "__main__":
    run_grpc_service()
    run_flask()
    run_streamlit()

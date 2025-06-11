from fastapi import FastAPI
from pydantic import BaseModel
import psutil
import datetime
import os 
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from scripts.pj.monitor import SystemMonitor
app = FastAPI()
monitor = SystemMonitor()

@app.get("/system-stats")
def read_system_stats():
    return monitor.get_stats()

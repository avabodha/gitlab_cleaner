import asyncio

import json

from cleaner.CleanupTask import close_session
from cleaner.Project import Project
from cleaner.start import starter
from datetime import datetime, timedelta

projects: Project = []

def load_tasks():
    global projects
    with open("tasks/prl.json") as f:
        data = json.load(f)

    for t in data:
        artifact_expire = str((datetime.utcnow() - timedelta(days=t["artifacts"]["older_than"])).strftime('%Y-%m-%dT%H:%M:%SZ'))
        artficts_after = None
        if t.get("artifacts").get("newer_than") != None:
            artficts_after = str((datetime.utcnow() - timedelta(days=(t.get("artifacts").get("newer_than")))).strftime('%Y-%m-%dT%H:%M:%SZ'))
        log_expire = str((datetime.utcnow() - timedelta(days=t["logs"]["older_than"])).strftime('%Y-%m-%dT%H:%M:%SZ'))
        pipeline_expire = str((datetime.utcnow() - timedelta(days=t["pipelines"]["older_than"])).strftime('%Y-%m-%dT%H:%M:%SZ'))
        
        p = Project(t.get("id"), t.get("name"), artifact_expire, log_expire, pipeline_expire, artficts_after)

        projects.append(p)

async def checker():
    global projects
    while True:
        tasks = len(asyncio.all_tasks())
        if tasks != 1:
            await asyncio.sleep(2)
        else:
            break
    
    for p in projects:
        print(p)
    await close_session()
    end =  datetime.now()

    print("Time taken: " + str(end - start) )

start = datetime.now()

load_tasks()
event_loop = asyncio.get_event_loop()

for p in projects:
    event_loop.run_until_complete(starter(p))
    
event_loop.run_until_complete(checker())

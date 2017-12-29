import n_server
import queue
import os
import uuid

lq = queue.Queue()
userList = {}

if os.path.exists('starteruuid.txt'):
    with open('starteruuid.txt','r') as f:
        uid= f.read()
else:
    uid = uuid.uuid4()

    with open('starteruuid.txt','w') as f:
        f.write(str(uid))

loggerThread = n_server.LoggerThread('LoggerTest',lq)
loggerThread.start()
sStarter = n_server.ServerStarterThread('ServerStarterTest',lq,userList,str(uid))
sStarter.start()

# listUpdater = n_server.ListUpdaterThread('ListUpdaterTest','0.0.0.0',lq,userList,)
# listUpdater.start()




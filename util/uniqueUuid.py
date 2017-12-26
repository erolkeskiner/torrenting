import os.path
import uuid


# checks if there is a uuid given before
# if there is takes it as uuid
# if not creates a new uuid and new file

uid = ''
if os.path.exists('uuid.txt'):
    with open('uuid.txt','r') as f:
        uid= f.read()
else:
    uid = uuid.uuid4()

    with open('uuid.txt','w') as f:
        f.write(str(uid))


# you can check it
# run the script it will create a new file
# if you run again you will see the same uuid

# delete uuid.txt file and re-run the script
# you will see a new uuid
print(uid)
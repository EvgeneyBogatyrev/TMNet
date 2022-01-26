import os
from pathlib import Path

with open("/model/models/modules/DCNv2/make.sh", 'w') as g:
    g.write("python3 setup.py build develop\n")

with open("/model/run.sh", 'w') as f:
    f.write("cd /model/models/modules/DCNv2\n")
    f.write("bash make.sh\n")

    videos = os.listdir("/dataset")
    for video in videos:
        f.write(f"mkdir /results/{video}\n")
        f.write(f"python3 /model/test_single_frame.py /dataset/{video} /results/{video}\n")
        f.write(f"rm -r /results/{video}/adobe\n")

os.system("chmod +x /model/run.sh")
os.system("/model/run.sh")

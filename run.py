import os
from pathlib import Path

with open("/model/models/modules/DCNv2/make.sh", 'w') as g:
    g.write("python3 setup.py build develop\n")

with open("run.sh", 'w') as f:
    f.write("cd /model/models/modules/DCNv2\n")
    f.write("bash make.sh\n")
    f.write("cd ../../../\n")
    #f.write("mkdir result\n")

    videos = os.listdir("/dataset")
    for video in videos:
        Path(f"/model/result/{video}").mkdir(parents=True, exist_ok=True)
        f.write(f"python3 test_single_frame.py /dataset/{video} /model/result/{video}\n")
        f.write(f"rm -r /model/result/{video}/adobe\n")
    f.write("chmod -R 0777 /model")

os.system("chmod +x run.sh")
os.system("./run.sh")

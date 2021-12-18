import os

with open("run.sh", 'w') as f:
    f.write("cd /model/models/modules/DCNv2\n")
    f.write("bash make.sh\n")
    f.write("cd ../../../\n")
    f.write("mkdir result\n")
    f.write("python3 test_multiple_frames.py /dataset /model/result\n")
    f.write("rm -r result/adobe\n")

os.system("./run.sh")

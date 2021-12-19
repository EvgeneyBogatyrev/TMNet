import os

with open("/model/models/modules/DCNv2/mak.sh", 'w') as g:
    g.write("python3 setup.py build develop\n")

with open("run.sh", 'w') as f:
    f.write("cd /model/models/modules/DCNv2\n")
    f.write("bash mak.sh\n")
    f.write("cd ../../../\n")
    f.write("mkdir result\n")
    f.write("python3 test_multiple_frames.py /dataset /model/result\n")
    f.write("rm -r result/adobe\n")
    f.write("chmod -R 0777 /model")

os.system("chmod +x run.sh")
os.system("./run.sh")

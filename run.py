import os

os.system("cd /model/models/modules/DCNv2")
os.system("bash make.sh")
os.system("cd ../../../")
os.system("mkdir result")
os.system("python3 test_multiple_frames.py /dataset /model/result")
os.system("rm -r result/adobe")

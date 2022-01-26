cd /model/models/modules/DCNv2
bash make.sh
mkdir /results/gauss
python3 /model/test_single_frame.py /dataset/gauss /results/gauss
rm -r /results/gauss/adobe
mkdir /results/bicubic
python3 /model/test_single_frame.py /dataset/bicubic /results/bicubic
rm -r /results/bicubic/adobe

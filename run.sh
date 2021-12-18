cd /model/models/modules/DCNv2
bash make.sh
cd ../../../
mkdir result
python3 test_multiple_frames.py /dataset /model/result
rm -r result/adobe

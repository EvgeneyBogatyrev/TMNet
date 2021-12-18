import os

root = '/main/mnt/calypso/24a_kir/MSU_VSR_Benchmark/input'

_, dirs, _ = next(os.walk(root))

for dir in dirs:
    if 'noise' in dir:
        os.system(f'python3 test_multiple_frames.py {root}/{dir} /main/mnt/calypso/25e_zim/VSR_noise/TMNet/{dir}')

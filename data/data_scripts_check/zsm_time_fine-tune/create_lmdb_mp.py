'''create lmdb files for Vimeo90K-7 frames training dataset (multiprocessing)
Will read all the images to the memory
'''

import os,sys
import os.path as osp
import glob
import pickle
from multiprocessing import Pool
import numpy as np
import lmdb
import cv2
try:
    sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
    import data.util as data_util
    import utils.util as util
except ImportError:
    pass

def reading_image_worker(path, key):
    '''worker for reading images'''
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return (key, img)

def vimeo7(args):
    '''create lmdb for the Vimeo90K-7 frames dataset, each image with fixed size
    GT: [3, 256, 448]
        Only need the 4th frame currently, e.g., 00001_0001_4
    LR: [3, 64, 112]
        With 1st - 7th frames, e.g., 00001_0001_1, ..., 00001_0001_7
    key:
        Use the folder and subfolder names, w/o the frame index, e.g., 00001_0001
    '''
    name = args['name']
    mode = args['mode']
    phase = args['phase']
    batch = args['batch']
    img_folder = args['img_folder']
    lmdb_save_path = args['lmdb_save_path']
    txt_file = args['txt_file']
    H_dst, W_dst = args['H_dst, W_dst']
    n_thread = args['n_thread']
    ori_format = args['ori_format']
    ########################################################
    if not lmdb_save_path.endswith('.lmdb'):
        raise ValueError("lmdb_save_path must end with \'lmdb\'.")
    #### whether the lmdb file exist
    if osp.exists(lmdb_save_path):
        print('Folder [{:s}] already exists. Exit...'.format(lmdb_save_path))
        sys.exit(1)

    #### read all the image paths to a list
    print('Reading image path list ...')
    with open(txt_file) as f:
        train_l = f.readlines()
        train_l = [v.strip() for v in train_l]
    all_img_list = []
    keys = []
    for line in train_l:
        folder = line.split('/')[0]
        try: 
            sub_folder = line.split('/')[1]
        except IndexError:
            sub_folder = ''

        file_l = glob.glob(osp.join(img_folder, folder, sub_folder) + '/*')
        all_img_list.extend(file_l)
        if sub_folder == '':
            j_len = len(file_l)
        else:
            j_len = 7
        for j in range(j_len):
            keys.append('{}_{}_{}'.format(folder, sub_folder, j + 1))
    all_img_list = sorted(all_img_list)
    keys = sorted(keys)
    if mode == 'GT': 
        all_img_list = [v for v in all_img_list if v.endswith(ori_format)]
        keys = [v for v in keys]
    print('Calculating the total size of images...')
    data_size = sum(os.stat(v).st_size for v in all_img_list)

    #### read all images to memory (multiprocessing)
    print('Read images with multiprocessing, #thread: {} ...'.format(n_thread))
    
    #### create lmdb environment
    env = lmdb.open(lmdb_save_path, map_size=data_size * 10)
    txn = env.begin(write=True)  # txn is a Transaction object

    #### write data to lmdb
    pbar = util.ProgressBar(len(all_img_list))

    i = 0
    for path, key in zip(all_img_list, keys):
        pbar.update('Write {}'.format(key))
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        key_byte = key.encode('ascii')
        H, W, C = img.shape  # fixed shape
        if H == H_dst and W == W_dst and C == 3:
            pass
        else:
            if H == W_dst and W == H_dst and C == 3:
                img = np.ascontiguousarray(np.transpose(img, (1, 0, 2)))
                H, W, C = img.shape
            else:
                print('Shape Error!')
                break
        # assert H == H_dst and W == W_dst and C == 3, 'different shape.'
        txn.put(key_byte, img)
        i += 1
        if  i % batch == 1:
            txn.commit()
            txn = env.begin(write=True)

    txn.commit()
    env.close()
    print('Finish reading and writing {} images.'.format(len(all_img_list)))
            
    print('Finish writing lmdb.')

    #### create meta information
    meta_info = {}
    if mode == 'GT':
        meta_info['name'] = name + phase + '_GT'
    elif mode == 'LR':
        meta_info['name'] = name + phase + '_LR7'
    meta_info['resolution'] = '{}_{}_{}'.format(3, H_dst, W_dst)
    key_set = set()
    for key in keys:
        a = key[:len(key) - (1 + len(key.split('_')[-2]) + 1 + len(key.split('_')[-1]))]
        b = key.split('_')[-2]
        # a, b, _ = key.split('_')
        key_set.add('{}_{}'.format(a, b))
    meta_info['keys'] = key_set
    pickle.dump(meta_info, open(osp.join(lmdb_save_path, name + phase + '_keys.pkl'), "wb"))
    print('Finish creating lmdb meta info.')
    return lmdb_save_path

def test_lmdb(dataroot, dataset='vimeo7'):
    env = lmdb.open(dataroot, readonly=True, lock=False, readahead=False, meminit=False)
    meta_info = pickle.load(open(osp.join(dataroot, 'Vimeo7_' + phase + '_keys.pkl'), "rb"))
    print('Name: ', meta_info['name'])
    print('Resolution: ', meta_info['resolution'])
    print('# keys: ', len(meta_info['keys']))
    # read one image
    if dataset == 'vimeo7':
        key = '00001_0001_4'
    else:
        raise NameError('Please check the filename format.')
    print('Reading {} for test.'.format(key))
    with env.begin(write=False) as txn:
        buf = txn.get(key.encode('ascii'))
    img_flat = np.frombuffer(buf, dtype=np.uint8)
    C, H, W = [int(s) for s in meta_info['resolution'].split('_')]
    img = img_flat.reshape(H, W, C)
    cv2.imwrite('test.png', img)


if __name__ == "__main__":
    #### configurations
    args = {}
    args['mode'] = 'GT'  # GT | LR
    args['phase'] = 'train'
    args['batch'] = 3000 # TODO: depending on your mem size
    args['img_folder'] = '/home/ubuntu/Disk/dataset/adobe240fps/visualization-360p/train_7f' # '/home/ubuntu/Dataset/davis16/vimeo90k-like/train/LR'
    args['lmdb_save_path'] = '/home/ubuntu/Disk/dataset/adobe240fps/visualization-360p/train_HR.lmdb' # '/home/ubuntu/Dataset/davis16/vimeo90k-like/train/train_LR.lmdb'
    args['txt_file'] = '/home/ubuntu/Disk/dataset/adobe240fps/visualization-360p/sep_trainlist.txt' # '/home/ubuntu/Dataset/davis16/vimeo90k-like/train/sep_trainlist.txt'
    args['H_dst, W_dst'] = 360, 640 # 90, 160 # 120, 213 # 480, 852
    args['n_thread'] = 40
    args['ori_format'] = '.png' # .png
    args['name'] = 'adobe240fps_' # Vimeo7_

    # args = {}
    # args['mode'] = 'LR'  # GT | LR
    # args['phase'] = 'train'
    # args['batch'] = 3000 # TODO: depending on your mem size
    # args['img_folder'] = '/home/ubuntu/Disk/dataset/adobe240fps/visualization-90p/train_7f' # '/home/ubuntu/Dataset/davis16/vimeo90k-like/train/LR'
    # args['lmdb_save_path'] = '/home/ubuntu/Disk/dataset/adobe240fps/visualization-90p/train_LR.lmdb' # '/home/ubuntu/Dataset/davis16/vimeo90k-like/train/train_LR.lmdb'
    # args['txt_file'] = '/home/ubuntu/Disk/dataset/adobe240fps/visualization-90p/sep_trainlist.txt' # '/home/ubuntu/Dataset/davis16/vimeo90k-like/train/sep_trainlist.txt'
    # args['H_dst, W_dst'] = 90, 160 # 120, 213 # 480, 852
    # args['n_thread'] = 40
    # args['ori_format'] = '.png' # .png
    # args['name'] = 'adobe240fps_' # Vimeo7_

    lmdb_file = vimeo7(args)
    # test_lmdb(lmdb_file, 'vimeo7')

from utils.evaluation_single_frame import test
import sys

test_args = {}

# DEFAULT =============================================================
test_args['cuda'] = '0'
test_args['code_name'] = 'TMNet'
test_args['model_path'] = '/model/checkpoints/tmnet_single_frame.pth'
test_args['result_folder'] = sys.argv[2]

# DATASET =============================================================
test_args['data_mode'] = 'adobe'
test_args['dataset_folder'] =  sys.argv[1]

# test_args['data_mode'] = 'vimeo_fast'
# test_args['dataset_folder'] =  './datasets/vimeo-90k_septuplet/fast_of_test/LR/*'

# test_args['data_mode'] = 'vimeo_medium'
# test_args['dataset_folder'] =  './datasets/vimeo-90k_septuplet/medium_of_test/LR/*'

# test_args['data_mode'] = 'vimeo_slow'
# test_args['dataset_folder'] =  './datasets/vimeo-90k_septuplet/slow_of_test/LR/*'

# TEST ================================================================
test(test_args)

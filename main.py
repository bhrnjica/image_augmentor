import sys, os, re, traceback
import multiprocessing.dummy

from os.path import isfile
from multiprocessing.dummy import Pool#, cpu_count
from counter import Counter
from ops.rotate import Rotate
from ops.fliph import FlipH
from ops.flipv import FlipV
from ops.zoom import Zoom
from ops.blur import Blur
from ops.noise import Noise
from ops.crop import Crop
from ops.resize import Resize
from ops.translate import Translate
from skimage.io import imread, imsave
from skimage import img_as_ubyte

EXTENSIONS = ['png', 'jpg', 'jpeg', 'bmp']
WORKER_COUNT = max(4 - 1, 1)
OPERATIONS = [Rotate, FlipH, FlipV, Translate, Noise, Zoom, Blur, Crop, Resize]

'''
Augmented files will have names matching the regex below, eg

    original__rot90__crop1__flipv.jpg

'''
AUGMENTED_FILE_REGEX = re.compile('^.*(__.+)+\\.[^\\.]+$')
EXTENSION_REGEX = re.compile('|'.join(map(lambda n : '.*\\.' + n + '$', EXTENSIONS)))


def build_augmented_file_name(original_name, ops):
    root, ext = os.path.splitext(original_name)
    result = root
    for op in ops:
        result += '__' + op.code
    return result + ext

def work(d, d_save, f, op_lists, counter):
    try:
        in_path = os.path.join(d,f)
        for op_list in op_lists:
            out_file_name = f if d_save != None and d != d_save else  build_augmented_file_name(f, op_list) 
            if isfile(os.path.join(d_save,out_file_name)):
                continue
            img = imread(in_path)
            for op in op_list:
                img = op.process(img)
            imsave(os.path.join(d_save, out_file_name),img_as_ubyte(img))

        counter.processed()
    except:
        traceback.print_exc(file=sys.stdout)

def process(tp, dir, dir_save, file, op_lists, counter):
    tp.apply_async(work, (dir,dir_save, file, op_lists, counter))


def process_images(image_dir, save_dir, op_codes):

    thread_pool = None
    counter = None

    op_lists = []
    for op_code_list in op_codes:
        op_list = []
        for op_code in op_code_list.split(','):
            op = None
            for op in OPERATIONS:
                op = op.match_code(op_code)
                if op:
                    op_list.append(op)
                    break
    
            if not op:
                print('Unknown operation {}'.format(op_code))
                sys.exit(3)
        op_lists.append(op_list)
    
    counter = Counter()
    thread_pool = Pool(WORKER_COUNT)
    print('Thread pool initialised with {} worker{}'.format(WORKER_COUNT, '' if WORKER_COUNT == 1 else 's'))
    
    matches = []
    for dir_info in os.walk(image_dir):
        dir_name, _, file_names = dir_info
        print('Processing {}...'.format(dir_name))
    
        for file_name in file_names:
            if EXTENSION_REGEX.match(file_name):
                if AUGMENTED_FILE_REGEX.match(file_name):
                    counter.skipped_augmented()
                else:
                    if save_dir == None:
                        save_dir = dir_name
                    process(thread_pool, dir_name, save_dir, file_name, op_lists, counter)
            else:
                counter.skipped_no_match()
    
    print ("Waiting for workers to complete...")
    thread_pool.close()
    thread_pool.join()
    return counter #, dir_info, matches, op_code_list, op_lists, thread_pool

if __name__ == '__main__':
    #staring image folder should be resized and cropped, and then performed image augemntation
    #image directory
    image_dir1 ='img-jan-20'

    #save directory
    save_dir1 = 'img'
    #resize and crop
    op_codes=['resize_212_202,crop_1_11_1_1']
    

    cnt = process_images(image_dir1, save_dir1, op_codes)
    print (cnt.get())

    #start image augmentation 
    dir1='img'
    dir2 = None
    op_codes1 = ['fliph', 'flipv','rot_10','rot_10', 'noise_0.01', 'noise_0.02', 'noise_0.05', 'trans_20_10','trans_-10_0','blur_1.5'
                'rot_10,fliph', 'rot_10,flipv', 'rot_10,noise_0.01', 'rot_10,noise_0.02', 'rot_10,noise_0.05', 'rot_10,trans_20_10','rot_10,trans_-10_0','rot_10,blur_1.5'
                'fliph,blur_1.5', 'flipv,blur_1.5','rot_10,blur_1.5','rot_10,blur_1.5', 'noise_0.01,blur_1.5', 'noise_0.02,blur_1.5', 'noise_0.05,blur_1.5', 'trans_20_10,blur_1.5','trans_-10_0,blur_1.5'
    ]
    cnt = process_images(dir1, dir2, op_codes1)
    print (cnt.get())



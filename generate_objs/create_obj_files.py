import os
import pickle
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--num_workers", default=3, type=int, required=False, help="Path to where the data should be saved")
args = parser.parse_args()

path_initial_jsons = '../../dataset/3D-FRONT'
des_path = 'export_objs'


previous_generated_data = pickle.load(open('houses_data.pkl', 'rb'))
json_files = [x['json_file'] + '.json' for x in previous_generated_data]
json_files = [x for x in json_files if not os.path.exists(des_path + os.sep + x.replace('.json', '.obj'))]

base_command = 'blenderproc run export_obj.py'

counter = [0]
counter_error = [0]
counter_lock = threading.Lock()
counter_error_lock = threading.Lock()


def proces_(jf):
    cur_path_json = path_initial_jsons + os.sep + jf
    cur_path_result = des_path + os.sep + jf.replace('.json', '.obj')

    os.makedirs(des_path, exist_ok=True)

    command = f"{base_command} --output_dir {cur_path_result} --front {cur_path_json}"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
    except:
        with counter_error_lock:
            counter_error[0] += 1


with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
    futures = {executor.submit(proces_, jf): jf for jf in json_files}
    for future in tqdm(as_completed(futures), total=len(futures)):
        try:
            future.result()
        except Exception as e:
            print(f"Error processing JSON: {e}")

import argparse
from snakeutils.files import readable_dir
import os
from multiprocessing.pool import ThreadPool
import subprocess
import tqdm

def run_soax(batch_soax,tif_dir,param_fp,output_dir):
    command = "{batch_soax} --image {tif_dir} --parameter {param_fp} --snake {output_dir}".format(
        batch_soax = batch_soax,
        tif_dir=tif_dir,
        param_fp=param_fp,
        output_dir=output_dir,
    )
    subprocess.call(command,shell=True, stdout=subprocess.PIPE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Try some parameters for snakes')
    parser.add_argument('batch_soax',help="Path to batch_soax executable")
    parser.add_argument('tif_dir',type=readable_dir,help='Directory with tif files to run in soax')
    parser.add_argument('params_dir',type=readabe_dir,help='Directory with soax param text files')
    parser.add_argument('output_dir',type=readable_dir,help='Directory to put')
    parser.add_argument('--workers', const=sum, default=5, type=int,
                    help='Number of batch_soax processes to have running at once')

    args = parser.parse_args()
    param_files = [filename for filename in os.listdir(args.params_dir) if filename.endswith(".txt")]
    param_files.sort()

    workers_num = args.workers

    soax_args = []
    for filename in param_files:
        param_fp = os.path.join(args.params_dir,filename)
        soax_args.append( [args.batch_soax,args.tif_dir,param_fp,args.output_dir] )

    with tqdm.tqdm(total=len(soax_args)) as pbar:
        with ThreadPool(workers_num) as pool:
            future = pool.map_async(run_soax, soax_args)
            while not future.ready():
                if counter.value != 0:
                    with counter_lock:
                        increment = counter.value
                        counter.value = 0
                    pbar.update(n=increment)
                time.sleep(1)
            result = future.get()



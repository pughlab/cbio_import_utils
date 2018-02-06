import os
import argparse
from string import Template

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--script_dir", type=str, required=True,
                        help="directory where qsub shell scripts stored")
    parser.add_argument("-m", "--vmem", type=int, required=False,
                        help="high vitual memory requested", default=12)
    parser.add_argument("-p", "--pe", type=int, required=False,
                        help="number of slots requested", default=1)
    parser.add_argument("-t", "--debug", action="store_true", required=False,
                        help="debug mode for testing")

    return parser.parse_args()

def main():
    args = get_options()

    for subdir, dirs, files in os.walk(args.script_dir):
        for file in files:
            if file.endswith(".sh"):
                sh_file = os.path.join(args.script_dir, file)
                print(sh_file)
                cmd = 'qsub -l mem_requested={0}G -l h_vmem={1}G -pe smp {2} {3}'.format(
                                args.vmem, args.vmem, args.pe, sh_file)
                print (cmd)
                if not args.debug:
                    os.system(cmd)

if __name__ == "__main__":
    main()
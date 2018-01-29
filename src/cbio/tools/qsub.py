import os
import argparse
from string import Template

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--script_dir", type=str,
                        help="directory where qsub shell scripts stored")
    parser.add_argument("-t", "--debug", action="store_true",
                        help="debug mode for testing")
    return parser.parse_args()

def main():
    args = get_options()

    for subdir, dirs, files in os.walk(args.script_dir):
        for file in files:
            if file.endswith(".sh"):
                sh_file = os.path.join(args.script_dir, file)
                print(sh_file)
                cmd = 'qsub %s'%sh_file
                print (cmd)
                if not args.debug:
                    os.system(cmd)
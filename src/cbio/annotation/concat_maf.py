import os
import argparse

def get_options():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="input vcf directory")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="maf output file including path")
    return parser.parse_args()

def main():
    args = get_options()
    count = 0
    with open(args.output, 'w') as of:
        for subdir, dirs, files in os.walk(args.input):
            for file in files:
                if not file.endswith(".maf"): continue
                with open(os.path.join(args.input, file)) as f:
            #         f.readline()
            #         header = f.readline().strip().split("\t")
            #         print (len(header))
            #         for idx,val in enumerate(header):
            #             print ("%s=>%s"%(idx,val))
            #         break
            # break
                    for line in f.readlines()[2:]:
                        try:
                            parts = line.strip().split("\t")
                            #print("length: 141=>%s" % len(parts))
                            #keep n_alt_count sample less than 3
                            if parts[44] and int(parts[44]) > 10: continue
                            #keep ExAc less than 0.4%
                            if parts[99] and float(parts[99])>= 0.004: continue
                            #keep genomeAD less than 0.1%
                            if parts[123] and float(parts[123]) >= 0.001: continue
                            for i in range(len(parts), 141):
                                parts.append('NA')
                            print (len(parts))
                            print (parts)
                            of.write("%s\n"%"\t".join(parts))
                        except:
                            print("Error length: 141=>%s" % len(parts))
                            count += 1
                            continue
    print ("total line skipped: %s"%count)
if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import os, sys, subprocess
import glob, argparse
from Bio import SeqIO
import pybedtools
from pybedtools import BedTool

def setup_outdir(outdir):

    path_out=os.path.abspath(outdir)

    if os.path.exists(path_out):
        reply=input("Overwrite existing output directory: "+path_out+"? [y/[n]] ")
        if reply=='y':
            os.system('rm -r '+ path_out)
            os.makedirs(path_out)
    else:
        os.makedirs(path_out)

    for subdir in ['clean', 'fixed']:
        if os.path.exists('{}/{}'.format(path_out, subdir)):
            pass
        else:
            os.makedirs('{}/{}'.format(path_out, subdir))
        
def string_to_bed(input_string):

    out_bed = BedTool(''.join(input_string), from_string=True)
    return(out_bed)

def fasta_to_bed(fasta_file):

    bed_string=[]

    with open(fasta_file):
        for record in SeqIO.parse(fasta_file, 'fasta'):
            bed_string.append('{} 0 {}\n'.format(record.id, len(record)))

    # out_bed = BedTool(''.join(bed_string), from_string=True)
    out_bed = string_to_bed(bed_string)

    return(out_bed)

def check_for_errors(fasta, search, outdir):

    errors = False

    # fasta_ext = os.path.splitext(os.path.basename(fasta))[1]
    name1 = os.path.splitext(os.path.basename(fasta))[0]
    name2 = name1.replace(".", "_")

    for error_file in glob.glob('{}/*'.format(search)):

        if name2.lower() in os.path.splitext(os.path.basename(error_file))[0].lower() :
            print('    Fixing errors in {}'.format(error_file))
            return(error_file)

    if not errors:
        print('    No errors in {}'.format(fasta))
        copy_cmd = 'cp {} {}/clean/{}'.format(fasta, outdir, os.path.basename(fasta))
        out = subprocess.run(copy_cmd, shell=True)

def parse_ncbi_error(input_file):

    error_lines = []
    extract = False

    with open(input_file, 'r') as f:
        for line in f.readlines():
            if line.rstrip('\n') == "Trim:":
                extract = True
            if extract and line != '':
                new_line = [i for n, i in enumerate(line.split('\t')) if n not in [1]]
                error_lines.append(' '.join(new_line).replace('..', ' ')) 

    out_bed = string_to_bed(error_lines[2:])

    return(out_bed)

def create_new_bed(mag_bed, ncbi_bed, mag_fasta, outdir, extension):

    # contigs in mag that don't overlap with ncbi errors
    ok_contigs = mag_bed.intersect(ncbi_bed, v=True)
    # contigs in mag that overlap with ncbi errors
    contigs_to_fix = mag_bed.intersect(ncbi_bed, wa=True)
    # subtracting overlapping regions from those contigs and splitting
    corrected_bed = contigs_to_fix.subtract(ncbi_bed)

    # fasta sequences for mag contigs not overlapping with ncbi errors
    nonoverlapping_fasta = ok_contigs.sequence(fi=mag_fasta, fullHeader=True)
    # fasta sequences for correct mag contigs that overlap with ncbi errors
    corrected_fasta = corrected_bed.sequence(fi=mag_fasta)

    file_prefix = os.path.splitext(os.path.basename(mag_fasta))[0]

    # bed file of the NCBI errors
    print('        - Creating BED summary of NCBI errors in MAG')
    ncbi_bed.saveas('{}/fixed/{}.errors.bed'.format(outdir, file_prefix))

    # specific to contigs that had NCBI errors removed
    print('        - Creating BED summary of corrected contigs in MAG')
    ok_contigs.saveas('{}/fixed/{}.fixed.bed'.format(outdir, file_prefix))

    # bed file of contigs in mag that were fine with no errors
    print('        - Creating BED summary of clean contigs MAG')
    corrected_bed.saveas('{}/fixed/{}.clean.bed'.format(outdir, file_prefix))

    # write both corrected contigs and ok contigs that did not overlap with
    # errors to FASTA File
    print('        - Creating FASTA for corrected MAGs')
    with open('{}/fixed/{}.new.{}'.format(outdir, file_prefix, extension), "w") as f:
        f.write((open(corrected_fasta.seqfn).read()))
        f.write((open(nonoverlapping_fasta.seqfn).read()))

def correct_mags(args):

    setup_outdir(args.output)

    for file in glob.glob('{}/*.{}'.format(args.mags, args.extension)):
        mag_errors = check_for_errors(file, args.errors, args.output)
    
        if mag_errors:
            mag_bed = fasta_to_bed(file)
            error_bed = parse_ncbi_error(mag_errors)
            create_new_bed(mag_bed, error_bed, file, args.output, args.extension)

def main():

    parser=argparse.ArgumentParser(description="Correct MAGs with NCBI submission errors")

    parser.add_argument('-m', '--mags_directory', type=str, required=True, dest='mags',
                        help='Directory of FASTA files of MAGs to correct.')

    parser.add_argument('-n', '--ncbi_errors', type=str, required=True, dest='errors',
                        help='Directory containing NCBI error files.')

    parser.add_argument('-e', '--fasta_extension', type=str, required=True, dest='extension',
                        help='Extension of MAG sequences')

    parser.add_argument('-o', '--output_directory', type=str, required=True, dest='output',
                        help='Directory to output corrected MAG files.')

    args=parser.parse_args()

    correct_mags(args)


    exit(0)

if __name__ == '__main__':
    main()

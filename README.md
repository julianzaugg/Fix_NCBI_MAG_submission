# Fix_NCBI_MAG_submission

Fix automated errors during the submission of MAGs to NCBI due to adaptors by removing problematic regions

```
usage: correct_mags.py [-h] -m MAGS -n ERRORS -e EXTENSION -o OUTPUT

python3 correct_mags.py \
    -m mags \
    -n ncbi_errors \
    -o corrected_mags \
    -e fasta
```

While processing MAGs, it will write to the stdout a list of which files it didn't find errors for and which it did. 

```
    No errors in mags/01_S196.metabat_sens.034_sub.fasta
    ERROR: ncbi_errors/remainingcontamination_01_s196_semibin_refined_071.txt
        - Creating BED summary of NCBI errors
        - Creating BED summary of corrected MAGs
        - Creating FASTA for corrected MAGs
    No errors in mags/04_S200.metabat_sspec.005.fasta
    No errors in mags/04_S200.semibin_refined.015.fasta
    No errors in mags/03V1_S199.metabat2_refined.056.fasta
    ERROR: ncbi_errors/remainingcontamination_05_s201_semibin_refined_083.txt
        - Creating BED summary of NCBI errors
        - Creating BED summary of corrected MAGs
        - Creating FASTA for corrected MAGs
```

In the output directory that is specified in the initial command, any MAGs without NCBI submission errors will be found in the `clean/` subdirectory. Each MAG with submission errors will have three output files in the `fixed/` subdirectory: (1) *.clean.bed, (2) *.clean.fasta, and (3) *.errors.bed.

```
corrected_mags/clean
    01_S196.concoct.009.fasta
    01_S196.metabat2_refined.015_sub.fasta
    01_S196.metabat2_refined.054_sub.fasta
    01_S196.metabat2_refined.069_sub.fasta
corrected_mags/fixed
    01_S196.maxbin.110.clean.bed
    01_S196.maxbin.110.clean.fasta
    01_S196.maxbin.110.errors.bed
    01_S196.metabat2_refined.075_sub.clean.bed
    01_S196.metabat2_refined.075_sub.clean.fasta
    01_S196.metabat2_refined.075_sub.errors.bed
    01_S196.metabat2_refined.083_sub.clean.bed
    01_S196.metabat2_refined.083_sub.clean.fasta
    01_S196.metabat2_refined.083_sub.errors.bed
    01_S196.metabat_sspec.024.clean.bed
```

The fixed sequences in *.clean.fasta will have unique IDs as the coordinates for the remaining regions are added to the FASTA header.

```
$ head corrected_mags/fixed/01_S196.maxbin.110.errors.bed
NODE_6161_length_7507_cov_1.353794      769     811     adaptor:NGB01029.1-not_cleaned
NODE_7420_length_6937_cov_1.424376      1530    1558    adaptor:NGB01114.1-not_cleaned

$ head corrected_mags/fixed/01_S196.maxbin.110.clean.bed
NODE_6161_length_7507_cov_1.353794      0       769
NODE_6161_length_7507_cov_1.353794      811     7507
NODE_7420_length_6937_cov_1.424376      0       1530
NODE_7420_length_6937_cov_1.424376      1558    6937

$ grep ">" corrected_mags/fixed/01_S196.maxbin.110.clean.fasta
>NODE_6161_length_7507_cov_1.353794:0-769
>NODE_6161_length_7507_cov_1.353794:811-7507
>NODE_7420_length_6937_cov_1.424376:0-1530
>NODE_7420_length_6937_cov_1.424376:1558-6937
```


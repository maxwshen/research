import sys
import string
import datetime
import random
import copy
import os
import commands
import find_read

from collections import defaultdict

def main():
  # input_folder = '/home/lin/nhood_files/'
  nhoods_fold = '/home/mshen/research/e_coli_nhoods_500_22.4_unwhole/'
  ec_fold = '/home/mshen/research/yu_ec_22.4_500_nhoods/'

  replace_reads_blasr(nhoods_fold, ec_fold)
  return


def replace_reads_blasr(nhoods_fold, ec_fold):
  blasr_exe = '/home/jeyuan/blasr/alignment/bin/blasr'
  blasr_options = '-bestn 1 -m 1'
  reads_file = '/home/mshen/research/data/PacBioCLR/PacBio_10kb_CLR_mapped_removed_homopolymers.fasta'

  ec_names = os.listdir(ec_fold)
  nh_names = os.listdir(nhoods_fold)
  d = build_hash(nh_names, ec_names)

  accuracy_cutoff = 80

  corrections = []

  for key in d:
    headers = []
    with open(nhoods_fold + d[key]) as f:
      lines = f.readlines()
      for line in lines:
        if line[0] == '>':
          headers.append(line.strip())
    for h in headers:
      full_read = find_read.find_read(h, reads_file)
      with open('temp.txt', 'w+') as f:
        f.write(full_read)
      blasr_out = commands.getstatusoutput(blasr_exe + ' ' + ec_fold + key + ' ' + 'temp.txt' + ' ' + blasr_options)[1]
      if len(blasr_out) > 0:
        accuracy = blasr_out.split()[5]
        nh_beg = blasr_out.split()[6]
        nh_end = blasr_out.split()[7]
        ec_beg = blasr_out.split()[9]
        ec_end = blasr_out.split()[10]
        if float(accuracy) > accuracy_cutoff:
          info = h + ' ' + nh_beg + ' ' + nh_end + ' ' + ec_fold + key + ' ' + ec_beg + ' ' + ec_end
          print info
          corrections.append(info)
  return corrections


def build_hash(nh_names, ec_names):
  # Builds a dict. Key = ec_file_name. Value = nh_name
  nh_names = sorted(nh_names)
  ec_names = sorted(ec_names)
  found = False
  d = dict()
  for i in range(len(ec_names)):
    for nh_name in nh_names:
      if ec_names[i][:20] == nh_name[:20]:
        d[ec_names[i]] = nh_name
        found = True
        break
    if found:
      nh_names.remove(d[ec_names[i]])
      found = False
  return d


if __name__ == '__main__':
  # Initiates program and records total time
  start = datetime.datetime.now()
  print 'Start:', start, '\n'
  main()
  end = datetime.datetime.now()
  print '\n\nEnd:', end, '\nTotal:', end - start
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2022 Junhao Yuan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import logging
import numpy as np
from mtscomp import compress

if len(sys.argv) != 2:
  print("Usage: compress.py <input_file>")
  sys.exit(1)

logging.basicConfig(filename='compress.log', encoding='utf-8' ,level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

walk_dir = sys.argv[1]

if not os.path.isdir(walk_dir):
  print("Invalid Directory: " + walk_dir)
  sys.exit(1)

for root, subdirs, files in os.walk(walk_dir):
  if '.phy' in subdirs:
    subdirs.remove('.phy')
    
  for file in files:
    if file.endswith('.bin'):
      logging.info('checking .meta for ' + file)
      # we found a file of type .bin to compress
      # if the meta file doesn't exist, we can't find out the info we need for compression
      meta_filename = file[:-4] + '.meta'
      if not os.path.exists(os.path.join(root, meta_filename)):
        logging.info('meta file is corrupt for ' + file)
        continue
      if os.path.exists(os.path.join(root, file[:-4] + '.cbin')):
        logging.debug('cbin file already exists for ' + file)
        continue
      
      # check the original binary file to see what type it is
      # so that we can check the correct sampling rate
      isImec = False
      if file.endswith('.ap.bin') or file.endswith('.lf.bin'):
        isImec = True
      
      # get the meta file and store the content into a dictionary for lookup
      meta_dict = {}
      try:
        with open(os.path.join(root, meta_filename), 'rb') as f:
          for line in f:
            (key, val) = line.rstrip().split(b'=')
            meta_dict[key.decode("utf-8")] = val.decode("utf-8")
      except:
        logging.info('meta file is corrupt for ' + file)
        continue
            
      
      # get the necessary metadata for compression
      md_dtype = np.int16
      md_channels = int(meta_dict['nSavedChans'])
      md_sample_rate = round(float(meta_dict['imSampRate'] if isImec else meta_dict['niSampRate']), -2)
      
      # compress the file, storing the result with the .cbin extension
      # stores the meta data in a file with the same name but with .ch extension
      # removes the original file after compression is done
      # MAKE SURE YOU HAVE A BACKUP OF THE ORIGINAL FILE BEFORE COMPRESSING
      compress(os.path.join(root, file), 
              os.path.join(root, file[:-4] + '.cbin'), 
              os.path.join(root, file[:-4] + '.ch'), 
              sample_rate=md_sample_rate, 
              n_channels=md_channels, 
              dtype=md_dtype)
      os.remove(os.path.join(root, file))
      logging.info(file + ' removed')
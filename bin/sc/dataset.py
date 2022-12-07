import torch
from torch.utils.data import DataLoader, Dataset
import numpy as np 
from librosa.util import find_files
from torchaudio import load
from torch import nn
import os 
# import IPython 
import pdb
import random
import torchaudio
import sys
import time

# Voxceleb 1 Speaker Identification
class SpeakerClassifiDataset(Dataset):
    def __init__(self, mode, file_path, meta_data, max_timestep=None):

        self.root = file_path
        self.speaker_num = 1251
        self.meta_data =meta_data
        self.max_timestep = max_timestep
        self.usage_list = open(self.meta_data, "r").readlines()
        self.dataset = eval("self.{}".format(mode))()        
        self.label = self.build_label(self.dataset)
        self.max_timestep = max_timestep
    
    # file_path/id0001/asfsafs/xxx.wav
    def build_label(self, train_path_list):

        y = []
        for path in train_path_list:
            id_string = path.split("/")[-3]
            y.append(int(id_string[2:]) - 10001)

        return y
    
    def train(self):
        dataset = []
        for string in self.usage_list:
            pair = string.split()
            index = pair[0]
            x = os.path.join(self.root, pair[1])
            if int(index) == 1:
                dataset.append(x)
        
                
        return dataset
        
    def dev(self):
        dataset = []
        for string in self.usage_list:
            pair = string.split()
            index = pair[0]
            x = os.path.join(self.root, pair[1])
            if int(index) == 2:
                dataset.append(x) 

        return dataset       

    def test(self):
        dataset = []
        for string in self.usage_list:
            pair = string.split()
            index = pair[0]
            x = os.path.join(self.root, pair[1])
            if int(index) == 3:
                dataset.append(x) 

        return dataset

    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        
        wav, sr = torchaudio.load(self.dataset[idx])
        wav = wav.squeeze(0)
        length = wav.shape[0]

        if self.max_timestep != None:
            if length > self.max_timestep:
                # start =torch.randint(0,length - self.max_timestep, (1,))
                start = 0
                wav = wav[start:start+self.max_timestep]
                length = self.max_timestep
    
        return wav, torch.tensor([length]), torch.tensor([self.label[idx]]).long()

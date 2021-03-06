#!/usr/bin/env python

import numpy as np


# function that collects the data wanted for use in the neural network
def process_showers(showers):
    List = []
    for shower in showers:
        Run    = shower.Run
        Energy = shower.Reconstruction.Energy
        Zen    = shower.Reconstruction.zen
        Type   = shower.Primary.Type
        
        cut_dist = 400
        
        TimeDelay = 0.
        Q         = 0.
        MuonVEM   = 0.
        nMuons    = 0.

        
        for i in range(len(shower.Signals.Tank)):
            if shower.Signals.LatDist[i] >= cut_dist and shower.Signals.TotalPE[i] != 0:
                totalVEM = shower.Signals.TotalVEM[i]
                totalPE  = shower.Signals.TotalPE[i]
                scale    = totalVEM/totalPE
                scaledPE = scale*shower.Signals.MuonPE[i]
                nMuons  += shower.Signals.nMuons[i]
                MuonVEM += scaledPE
                if totalVEM >= 0.6 and totalVEM <= 2.0:
                    TimeDelay += np.abs(shower.Signals.TimeDelay[i])
                    Q += totalVEM

        List.append([Run,Energy,Zen,TimeDelay,Q,MuonVEM,nMuons,Type])
    return List

# function that avarages the NN data for each run
def avg_runs(List,Type):
    
    avgList = []
    
    run_list = set()
    for shower in List:
        run_list.add(shower[0])
    
    for Run in run_list:
        nShowers      = 0.
        Energy_tot    = 0.
        Zen_tot       = 0.
        TimeDelay_tot = 0.
        Q_tot         = 0.
        MuonVEM_tot   = 0.
        nMuons_tot    = 0.
        for shower in List:
            if shower[0] == Run:
                nShowers      += 1.
                Energy_tot    += shower[1]
                Zen_tot       += shower[2]
                TimeDelay_tot += shower[3]
                Q_tot         += shower[4]
                MuonVEM_tot   += shower[5]
                nMuons_tot    += shower[6]
                
        Energy_avg    = Energy_tot/nShowers
        Zen_avg       = Zen_tot/nShowers
        TimeDelay_avg = TimeDelay_tot/nShowers
        Q_avg         = Q_tot/nShowers
        MuonVEM_avg   = MuonVEM_tot/nShowers
        nMuons_avg    = nMuons_tot/nShowers
        avgList.append([Run,Energy_avg,Zen_avg,TimeDelay_avg,Q_avg,MuonVEM_avg,nMuons_avg,Type])
    
    return avgList


# first the proton data
protondata = np.load('./data/proton_showers.npy')
NNdata_proton = process_showers(protondata) # original data
del protondata # to save memory
NNdata_proton_avg = avg_runs(NNdata_proton,"PPlus") # average by run number

# now the iron data
irondata = np.load('./data/iron_showers.npy')
NNdata_iron = process_showers(irondata) # original data
del irondata # to save memory
NNdata_iron_avg = avg_runs(NNdata_iron,'Fe56Nucleus') # average by run number

# combine proton and iron
NNdata     = np.concatenate((NNdata_proton,NNdata_iron))
NNdata_avg = np.concatenate((NNdata_proton_avg,NNdata_iron_avg))



# save the data

print 'saving ./data/NN_data.npy'
np.save('./data/NN_data.npy',NNdata)

print 'saving ./data/NN_data_avg.npy'
np.save('./data/NN_data_avg.npy',NNdata_avg)

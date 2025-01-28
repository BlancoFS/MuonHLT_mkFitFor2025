# CMS Run 3 Muon HLT

## CMSSW_14_2_X (mkFit customization)

### Setup
```shell
export SCRAM_ARCH=el8_amd64_gcc12
cmsrel CMSSW_14_2_1
cd CMSSW_14_2_1/src
cmsenv
git cms-init

git cms-merge-topic mmasciov:142X_hltPixelAutoTuning
git cms-merge-topic mmasciov:142X_mkFitForHLT_stripSpeedup
git clone https://github.com/cms-data/RecoTracker-MkFit.git RecoTracker/MkFit/data
git clone -b Run2024 https://github.com/BlancoFS/MuonHLT_mkFitFor2025.git
cp customizeHLTIter0ToMkFit.py RecoTracker/MkFit/python/

scram b -j 8
```

### HLT menu for Data 2024
```shell
hltGetConfiguration /dev/CMSSW_14_2_0/GRun \
 --process MYHLT \
 --data --globaltag 141X_dataRun3_HLT_v2 \
 --unprescale \
 --paths \
HLTriggerFirstPath,\
HLT_IsoMu24_v*,\
HLT_Mu50_v*,\
HLT_CascadeMu100_v*,\
HLT_HighPtTkMu100_v*,\
HLT_Mu15_v*,\
HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8_v*,\
HLTriggerFinalPath,\
HLTAnalyzerEndpath \
 --input /store/data/Run2024I/Muon0/RAW-RECO/ZMu-PromptReco-v1/000/386/478/00000/1356a098-a037-43c9-a9e0-8d1302fb791b.root \
 --eras Run3 \
 --max-events -1 \
 --full --offline --no-output \
 --customise \
 HLTrigger/Configuration/customize_CAPixelOnlyRetune.customize_CAPixelOnlyRetune,\
 RecoTracker/MkFit/customizeHLTIter0ToMkFit.customizeHLTIter0ToMkFit,\
 RecoTracker/MkFit/customizeHLTIter0ToMkFit.customizeHLTIter0HighPtTkMuToMkFit,\
 RecoTracker/MkFit/customizeHLTIter0ToMkFit.customizeIterTrackL3MuonIter0_forMuonIso,\
 RecoTracker/MkFit/customizeHLTIter0ToMkFit.customizeHLTIter0ForIterL3FromL1MuonToMkFit,\
 RecoTracker/MkFit/customizeHLTIter0ToMkFit.customizeHLTIter0ForIterL3Muon \
 --full --offline --no-output >hlt_muon_data.py
```
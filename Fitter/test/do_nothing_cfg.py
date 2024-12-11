import FWCore.ParameterSet.Config as cms
process = cms.Process("MAIN")

process.source = cms.Source("EmptySource")
process.options = cms.untracked.PSet()
# More threads if asking for more than 1 core in custom_crab.py
#process.options.numberOfThreads=cms.untracked.uint32(4)

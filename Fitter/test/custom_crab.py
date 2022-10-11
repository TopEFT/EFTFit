import os

def custom_crab(config):
    print '>> Customising the crab config'
    ''' Uncomment for earth '''
    #from CRABClient.UserUtilities import getUsernameFromSiteDB
    #config.Site.storageSite = 'T3_US_NotreDame'
    #config.Site.blacklist = ['T3_IT_Bologna', 'T3_US_UMiss', 'T2_ES_IFCA', 'T2_TR_METU', 'T2_CH_CSCS', 'T3_US_Baylor', 'T3_FR_IPNL', 'T3_UK_London_RHUL', 'T3_KR_KNU', 'T3_UK_London_QMUL', 'T2_FR_GRIF_IRFU', 'T2_FR_GRIF_LLR', 'T2_BE_IIHE', 'T3_UK_ScotGrid_GLA','T2_PT_NCG_Lisbon','T2_TW_NCHC']
    ''' end uncomment '''
    #config.Data.outLFNDirBase = '/store/user/%s/EFT/' % (getUsernameFromSiteDB())
    config.JobType.psetName = os.environ['CMSSW_BASE']+'/src/EFTFit/Fitter/test/do_nothing_cfg.py'
    config.General.transferLogs = True
    config.Data.outLFNDirBase = '/store/user/byates/EFT/' # REPLACE with your username
    config.JobType.maxMemoryMB = 8000 # Request 5000 MB of RAM (works for 64 2D scan points per job)
    config.JobType.numCores = 4

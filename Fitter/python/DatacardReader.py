import os
import math
import logging
import CombineHarvester.CombineTools.ch as ch
from utils import regex_match,run_command

class DatacardReader(object):
    DUMMY_UP = -999
    DUMMY_DOWN = -999

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.card_path = ""
        self.is_loaded = False
        self.modified_systs = False

        # Options for cb.ParseDatacard()
        self.load_ops = {
            'analysis': 'EFT',
            'era': '13TeV',
            'mass': '125',
            'channel': "",
            'bin_id': 0
        }

    # Load a datacard from text file
    def load(self,fpath):
        # Returns: None
        if not os.path.exists(fpath):
            return
        self.cb = ch.CombineHarvester()
        self.cb.ParseDatacard(fpath,**self.load_ops)
        self.card_path = fpath
        self.is_loaded = True
        self.modified_systs = False

    # Write the datacard to a text file
    def write(self,outf):
        # Returns: None
        self.cb.WriteDatacard(outf)
        if self.modified_systs:
            # Replace any dummy systematics in the datacard if needed
            #TODO: Probably want to handle the case were a systematic has been
            #      removed from all processes in all bins, but seems to be harmless
            tar_str = "%d/%d" % (self.DUMMY_DOWN,self.DUMMY_UP)
            rep_str = "-".ljust(len(tar_str))
            run_command(['sed','-i','-e',"s|%s|%s|g" % (tar_str,rep_str),outf])

    def hasCard(self):
        # Returns: bool
        return self.is_loaded

    def getBins(self,keep=[]):
        # Returns: set(str)
        if len(keep):
            return regex_match(self.cb.bin_set(),keep)
        else:
            return self.cb.bin_set()

    def getProcs(self,keep=[]):
        # Returns: set(str)
        if len(keep):
            return regex_match(self.cb.process_set(),keep)
        else:
            return self.cb.process_set()

    def getSysts(self,keep=[]):
        # Returns: set(str)
        if len(keep):
            return regex_match(self.cb.syst_name_set(),keep)
        else:
            return self.cb.syst_name_set()

    # Super adhoc way to remove a systematic from the datacard
    def removeSyst(self,procs,bins,syst_name):
        # Returns: None
        # NOTE: It is very important to call write() and load() on the datacard
        #       after removing a systematic, otherwise the self.cb object will
        #       have dummy values floating around for the removed systematics.
        def f(s):
            m1 = len(regex_match([s.bin()],regex_lst=bins))
            m2 = len(regex_match([s.process()],regex_lst=procs))
            m3 = len(regex_match([s.name()],regex_lst=[syst_name]))
            if m1 and m2 and m3:
                self.logger.info("Removing Systematic: %s - %s - %s",s.name().ljust(10),s.process().ljust(5),s.bin())
                s.set_asymm(1)
                s.set_value_u(self.DUMMY_UP)
                s.set_value_d(self.DUMMY_DOWN)
        self.modified_systs = True
        self.cb.ForEachSyst(f)

    # Filter out entire bins from the datacard
    def filterBins(self,bins):
        bin_str = [str(x).ljust(10) for x in bins]
        bin_str = '[' + ', '.join(bin_str) + ']'
        self.logger.info("Keeping bins that match any of: %s",bin_str)
        bin_lst = self.getBins(keep=bins)
        self.cb.bin(bin_lst)

    # Add new systematic parameter after the fact
    def addSyst(self,procs,bins,syst_name,val_u,val_d=None,syst_type='lnN'):
        # procs: List of processes to apply the systematic to
        # bins: List of bins to apply the systematic to
        # syst_name: Name of the systematic that will appear in the datacard
        # val_u: The symm error or the asymm upper error
        # val_d: The asymm lower error
        # syst_type: The type of systematic (e.g. log-normal, etc.)
        colw = 10

        syst_str = syst_name.ljust(10)

        bin_str = [str(x).ljust(10) for x in bins]
        bin_str = '[' + ', '.join(bin_str) + ']'

        proc_str = [str(x).ljust(5) for x in procs]
        proc_str = '[' + ', '.join(proc_str) + ']'

        bin_lst  = self.getBins(keep=bins)
        proc_lst = self.getProcs(keep=procs)

        self.logger.info("Adding Systematic: %s - %s - %s",syst_str,proc_str,bin_str)
        if val_d is None:   # Symmetric error
            self.cb.cp().process(proc_lst).bin(bin_lst).AddSyst(self.cb,syst_name,syst_type,ch.SystMap()(val_u))
        else: # Asymmetric error
            self.cb.cp().process(proc_lst).bin(bin_lst).AddSyst(self.cb,syst_name,syst_type,ch.SystMap()(val_d,val_u))
        self.modified_systs = True  # This is not really needed as it is only used to trigger the string replacement of removed systematics

    def getMaxBinRate(self,keep=[]):
        # Returns: str
        max_bin = ''
        max_val = 0.0
        for b in self.getBins(keep=['.*']):
            r = self.getBinRate(b,keep)
            if r > max_val:
                max_val = r
                max_bin = b
        return max_bin

    def getBinRate(self,b,keep=[]):
        # Returns: float
        tmp = self.cb.cp()
        tmp.bin([b])
        if len(keep): tmp.process(keep)
        return tmp.GetRate()

    def getBinUncertainty(self,b,keep=[]):
        # Returns: float
        tmp = self.cb.cp()
        tmp.bin([b])
        if len(keep): tmp.process(keep)
        return tmp.GetUncertainty()

    def getBinSensitivity(self,b,signals):
        # Returns: float
        bkgs = [x for x in self.getProcs() if x not in signals]
        sig_rate = self.getBinRate(b,signals)
        bkg_rate = self.getBinRate(b,bkgs)
        return sig_rate / math.sqrt(bkg_rate)

if __name__ == "__main__":
    cmssw_base = "/afs/crc.nd.edu/user/a/awightma/CMSSW_Releases/CMSSW_8_1_0/"
    input_dir  = "src/EFTFit/Fitter/test/anatest14/SM_impacts_AsimovSMdata/"
    dc_name    = "EFT_MultiDim_Datacard.txt"
    fpath = os.path.join(cmssw_base,input_dir,dc_name)

    reader = DatacardReader()
    reader.load(fpath)

    bins_all = ['.*']
    bins_2lss_all = ['C_2lss_.*']
    bins_3l_all   = ['C_3l_.*']
    bins_4l_all   = ['C_4l_.*']

    bins_3l_mix   = ['C_3l_mix_[pm]_.*']
    bins_3l_sfz   = ['C_3l_mix_sfz_.*']

    for b in reader.getBins(keep=bins_all):
        continue
        tmp = reader.cb.cp()
        tmp.bin([b])
        tmp.PrintProcess()
        print "%s: %.3f +/- %.3f" % (b.ljust(21),tmp.GetRate(),tmp.GetUncertainty())

    rm_systs = ['^PDF$','^MUF$']    # Remove these systematics from all processes in all bins
    for syst in rm_systs: reader.removeSyst(b='.*',proc='.*',syst_name=syst)
    reader.write(fpath); reader.load(fpath)
#ifndef PLOTDATA_H_
#define PLOTDATA_H_

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <set>
#include <map>
#include <unordered_map>
#include <utility>
#include <stdio.h>
#include <math.h>
#include <dirent.h>

#include "TString.h"

typedef std::vector<TString> vTStr;

vTStr ALL_PROCS {
    "charge_flips","fakes",
    "Diboson","Triboson",
    "convs","tWZ",
    "ttH","ttll","ttlnu","tllq","tHq","tttt"
};

vTStr YIELD_TABLE_ORDER {
    "Diboson","Triboson","charge_flips","fakes","convs",
    "ttlnu","ttll","ttH","tllq","tHq","tttt"
};

vTStr WC_list = {"ctW", "ctZ", "ctp", "cpQM", "ctG", "cbW", "cpQ3", 
                 "cptb", "cpt", "cQl3i", "cQlMi", "cQei", "ctli", 
                 "ctei", "ctlSi", "ctlTi", "cQq13", "cQq83", "cQq11", 
                 "ctq1", "cQq81", "ctq8", "ctt1", "cQQ1", "cQt8", "cQt1"};

vTStr SIG_PROCS {"ttlnu", "ttll", "ttH", "tllq", "tHq", "tttt"};

vTStr BKGD_PROCS {"Diboson", "Triboson", "charge_flips", "fakes", "convs", "tWZ"};

// adding 3l-offZ division event categories
vTStr SR_list = {"2lss_p", "2lss_m", "2lss_4t_p", "2lss_4t_m", "3l_p_offZ_low_1b", "3l_p_offZ_high_1b", "3l_p_offZ_none_1b", "3l_m_offZ_low_1b", "3l_m_offZ_high_1b", "3l_m_offZ_none_1b", "3l_p_offZ_low_2b", "3l_p_offZ_high_2b", "3l_p_offZ_none_2b", "3l_m_offZ_low_2b", "3l_m_offZ_high_2b", "3l_m_offZ_none_2b", "3l_onZ_1b", "3l_onZ_2b", "4l"};

// include onZ split
vTStr SR_list_onZsplit = {"2lss_p", "2lss_m", "2lss_4t_p", "2lss_4t_m", "3l_p_offZ_low_1b", "3l_p_offZ_high_1b", "3l_p_offZ_none_1b", "3l_m_offZ_low_1b", "3l_m_offZ_high_1b", "3l_m_offZ_none_1b", "3l_p_offZ_low_2b", "3l_p_offZ_high_2b", "3l_p_offZ_none_2b", "3l_m_offZ_low_2b", "3l_m_offZ_high_2b", "3l_m_offZ_none_2b", "3l_onZ_2b_2j3j", "4l", "3l_onZ_1b", "3l_onZ_2b_4j5j"};

vTStr SR_list_3 = {"2lss_p", "2lss_m", "2lss_4t", "3l_offZ", "3l_onZ_2b_2j3j", "4l", "3l_onZ_1b", "3l_onZ_2b_4j5j"};

vTStr SR_list_2lss = {"2lss_p", "2lss_m", "2lss_4t_p", "2lss_4t_m"};

// pick from the above list to plot data
vTStr SR_list_2 = SR_list_onZsplit;


std::vector<std::string> kin_list = {"ht"};//{"lj0pt", "ptz"};

std::unordered_map<std::string,std::vector<TString> > cat_groups {
    {"all",
      {
        "2lss_p_4j",
        "2lss_p_5j",
        "2lss_p_6j",
        "2lss_p_7j",
        "2lss_m_4j",
        "2lss_m_5j",
        "2lss_m_6j",
        "2lss_m_7j",
        "2lss_4t_p_4j",
        "2lss_4t_p_5j",
        "2lss_4t_p_6j",
        "2lss_4t_p_7j",
        "2lss_4t_m_4j",
        "2lss_4t_m_5j",
        "2lss_4t_m_6j",
        "2lss_4t_m_7j",
        "3l_p_offZ_low_1b_2j",
        "3l_p_offZ_low_1b_3j",
        "3l_p_offZ_low_1b_4j",
        "3l_p_offZ_low_1b_5j",
        "3l_m_offZ_low_1b_2j",
        "3l_m_offZ_low_1b_3j",
        "3l_m_offZ_low_1b_4j",
        "3l_m_offZ_low_1b_5j",
        "3l_p_offZ_low_2b_2j",
        "3l_p_offZ_low_2b_3j",
        "3l_p_offZ_low_2b_4j",
        "3l_p_offZ_low_2b_5j",
        "3l_m_offZ_low_2b_2j",
        "3l_m_offZ_low_2b_3j",
        "3l_m_offZ_low_2b_4j",
        "3l_m_offZ_low_2b_5j",
        "3l_p_offZ_high_1b_2j",
        "3l_p_offZ_high_1b_3j",
        "3l_p_offZ_high_1b_4j",
        "3l_p_offZ_high_1b_5j",
        "3l_m_offZ_high_1b_2j",
        "3l_m_offZ_high_1b_3j",
        "3l_m_offZ_high_1b_4j",
        "3l_m_offZ_high_1b_5j",
        "3l_p_offZ_high_2b_2j",
        "3l_p_offZ_high_2b_3j",
        "3l_p_offZ_high_2b_4j",
        "3l_p_offZ_high_2b_5j",
        "3l_m_offZ_high_2b_2j",
        "3l_m_offZ_high_2b_3j",
        "3l_m_offZ_high_2b_4j",
        "3l_m_offZ_high_2b_5j",
        "3l_p_offZ_none_1b_2j",
        "3l_p_offZ_none_1b_3j",
        "3l_p_offZ_none_1b_4j",
        "3l_p_offZ_none_1b_5j",
        "3l_m_offZ_none_1b_2j",
        "3l_m_offZ_none_1b_3j",
        "3l_m_offZ_none_1b_4j",
        "3l_m_offZ_none_1b_5j",
        "3l_p_offZ_none_2b_2j",
        "3l_p_offZ_none_2b_3j",
        "3l_p_offZ_none_2b_4j",
        "3l_p_offZ_none_2b_5j",
        "3l_m_offZ_none_2b_2j",
        "3l_m_offZ_none_2b_3j",
        "3l_m_offZ_none_2b_4j",
        "3l_m_offZ_none_2b_5j",
        "3l_onZ_1b_2j",
        "3l_onZ_1b_3j",
        "3l_onZ_1b_4j",
        "3l_onZ_1b_5j",
        "3l_onZ_2b_2j",
        "3l_onZ_2b_3j",
        "3l_onZ_2b_4j",
        "3l_onZ_2b_5j",
        "4l_2j_2b",
        "4l_3j_2b",
        "4l_4j_2b",
      }
    },
    {"2lss_4t_m",
      {
        "2lss_4t_m_4j",
        "2lss_4t_m_5j",
        "2lss_4t_m_6j",
        "2lss_4t_m_7j",
      }
    },
    {"2lss_4t_p",
      {
        "2lss_4t_p_4j",
        "2lss_4t_p_5j",
        "2lss_4t_p_6j",
        "2lss_4t_p_7j",
      }
    },
    {"2lss_m",
      {
        "2lss_m_4j",
        "2lss_m_5j",
        "2lss_m_6j",
        "2lss_m_7j",
      }
    },
    {"2lss_p",
      {
        "2lss_p_4j",
        "2lss_p_5j",
        "2lss_p_6j",
        "2lss_p_7j",
      }
    },
    {"3l_m_offZ_low_1b",
      {
        "3l_m_offZ_low_1b_2j",
        "3l_m_offZ_low_1b_3j",
        "3l_m_offZ_low_1b_4j",
        "3l_m_offZ_low_1b_5j",
      }
    },
    {"3l_m_offZ_high_1b",
      {
        "3l_m_offZ_high_1b_2j",
        "3l_m_offZ_high_1b_3j",
        "3l_m_offZ_high_1b_4j",
        "3l_m_offZ_high_1b_5j",
      }
    },
    {"3l_m_offZ_none_1b",
      {
        "3l_m_offZ_none_1b_2j",
        "3l_m_offZ_none_1b_3j",
        "3l_m_offZ_none_1b_4j",
        "3l_m_offZ_none_1b_5j",
      }
    },
    {"3l_m_offZ_low_2b",
      {
        "3l_m_offZ_low_2b_2j",
        "3l_m_offZ_low_2b_3j",
        "3l_m_offZ_low_2b_4j",
        "3l_m_offZ_low_2b_5j",
      }
    },
    {"3l_m_offZ_high_2b",
      {
        "3l_m_offZ_high_2b_2j",
        "3l_m_offZ_high_2b_3j",
        "3l_m_offZ_high_2b_4j",
        "3l_m_offZ_high_2b_5j",
      }
    },
    {"3l_m_offZ_none_2b",
      { "3l_m_offZ_none_2b_2j",
        "3l_m_offZ_none_2b_3j",
        "3l_m_offZ_none_2b_4j",
        "3l_m_offZ_none_2b_5j",
      }
    },
    {"3l_p_offZ_low_1b",
      {
        "3l_p_offZ_low_1b_2j",
        "3l_p_offZ_low_1b_3j",
        "3l_p_offZ_low_1b_4j",
        "3l_p_offZ_low_1b_5j",
      }
    },
    {"3l_p_offZ_high_1b",
      { "3l_p_offZ_high_1b_2j",
        "3l_p_offZ_high_1b_3j",
        "3l_p_offZ_high_1b_4j",
        "3l_p_offZ_high_1b_5j",
      }
    },
    {"3l_p_offZ_none_1b",
      { "3l_p_offZ_none_1b_2j",
        "3l_p_offZ_none_1b_3j",
        "3l_p_offZ_none_1b_4j",
        "3l_p_offZ_none_1b_5j",
      }
    },
    {"3l_p_offZ_low_2b",
      {
        "3l_p_offZ_low_2b_2j",
        "3l_p_offZ_low_2b_3j",
        "3l_p_offZ_low_2b_4j",
        "3l_p_offZ_low_2b_5j",
      }
    },
    {"3l_p_offZ_high_2b",
      { "3l_p_offZ_high_2b_2j",
        "3l_p_offZ_high_2b_3j",
        "3l_p_offZ_high_2b_4j",
        "3l_p_offZ_high_2b_5j",
      }
    },
    {"3l_p_offZ_none_2b",
      { "3l_p_offZ_none_2b_2j",
        "3l_p_offZ_none_2b_3j",
        "3l_p_offZ_none_2b_4j",
        "3l_p_offZ_none_2b_5j",
      }
    },
    {"3l_onZ_1b",
      {
        "3l_onZ_1b_2j",
        "3l_onZ_1b_3j",
        "3l_onZ_1b_4j",
        "3l_onZ_1b_5j",
      }
    },
    {"3l_onZ_2b",
      {
        "3l_onZ_2b_2j",
        "3l_onZ_2b_3j",
        "3l_onZ_2b_4j",
        "3l_onZ_2b_5j",
      }
    },
    {"4l",
      {
        "4l_2j",
        "4l_3j",
        "4l_4j",
      }
    },
    
    {"3l_onZ_2b_2j3j",
      {
        "3l_onZ_2b_2j",
        "3l_onZ_2b_3j",
      }
    },
    {"3l_onZ_2b_4j5j",
      {
        "3l_onZ_2b_4j",
        "3l_onZ_2b_5j",
      }
    },
    
    {"2lss_4t",
      {
        "2lss_4t_p_4j",
        "2lss_4t_p_5j",
        "2lss_4t_p_6j",
        "2lss_4t_p_7j",
        
        "2lss_4t_m_4j",
        "2lss_4t_m_5j",
        "2lss_4t_m_6j",
        "2lss_4t_m_7j",
      }
    },
    
    {"3l_offZ",
      {
        "3l_p_offZ_low_1b_2j",
        "3l_p_offZ_low_1b_3j",
        "3l_p_offZ_low_1b_4j",
        "3l_p_offZ_low_1b_5j",
        "3l_p_offZ_high_1b_2j",
        "3l_p_offZ_high_1b_3j",
        "3l_p_offZ_high_1b_4j",
        "3l_p_offZ_high_1b_5j",
        "3l_p_offZ_none_1b_2j",
        "3l_p_offZ_none_1b_3j",
        "3l_p_offZ_none_1b_4j",
        "3l_p_offZ_none_1b_5j",
        
        "3l_m_offZ_low_1b_2j",
        "3l_m_offZ_low_1b_3j",
        "3l_m_offZ_low_1b_4j",
        "3l_m_offZ_low_1b_5j",
        "3l_m_offZ_high_1b_2j",
        "3l_m_offZ_high_1b_3j",
        "3l_m_offZ_high_1b_4j",
        "3l_m_offZ_high_1b_5j",
        "3l_m_offZ_none_1b_2j",
        "3l_m_offZ_none_1b_3j",
        "3l_m_offZ_none_1b_4j",
        "3l_m_offZ_none_1b_5j",
        
        "3l_p_offZ_low_2b_2j",
        "3l_p_offZ_low_2b_3j",
        "3l_p_offZ_low_2b_4j",
        "3l_p_offZ_low_2b_5j",
        "3l_p_offZ_high_2b_2j",
        "3l_p_offZ_high_2b_3j",
        "3l_p_offZ_high_2b_4j",
        "3l_p_offZ_high_2b_5j",
        "3l_p_offZ_none_2b_2j",
        "3l_p_offZ_none_2b_3j",
        "3l_p_offZ_none_2b_4j",
        "3l_p_offZ_none_2b_5j",
        
        "3l_m_offZ_low_2b_2j",
        "3l_m_offZ_low_2b_3j",
        "3l_m_offZ_low_2b_4j",
        "3l_m_offZ_low_2b_5j",
        "3l_m_offZ_high_2b_2j",
        "3l_m_offZ_high_2b_3j",
        "3l_m_offZ_high_2b_4j",
        "3l_m_offZ_high_2b_5j",
        "3l_m_offZ_none_2b_2j",
        "3l_m_offZ_none_2b_3j",
        "3l_m_offZ_none_2b_4j",
        "3l_m_offZ_none_2b_5j",
      }
    },
};

struct PlotData {
    std::vector<TString> SR_name;
    std::vector<double> data;
    std::vector<double> sum;
    std::vector<double> err;
    std::unordered_map<std::string, std::vector<double> > procs;
    std::unordered_map<std::string, std::vector<double> > procs_error;
    PlotData() {
        SR_name = {};
        data = {};
        sum = {};
        err = {};
        for (TString proc: ALL_PROCS) {
            procs[proc.Data()] = {};
        }
        for (TString proc: ALL_PROCS) {
            procs_error[proc.Data()] = {};
        }
    }
};

std::vector<std::string> stringSplit(std::string str, std::string delimiter) {
    std::vector<std::string> substrs = {};
    size_t pos = 0;
    while ((pos = str.find(delimiter)) != std::string::npos) {
        substrs.push_back(str.substr(0, pos));
        str.erase(0, pos + delimiter.length());
    }
    return substrs;
}

PlotData assign(PlotData taker, PlotData giver, int ig) {
    if (ig >= giver.SR_name.size()) {
        cout << "Assigning index: " << ig << endl;
        cout << "The range of the giver PlotData: " << giver.SR_name.size() << endl;
        cout << "Last element of giver PlotData: " << giver.SR_name[ig-1] << endl;
        cout << "[ERROR] Index out of bound used in assigning." << endl;
        throw;
    }
    taker.SR_name.push_back(giver.SR_name[ig]);
    taker.data.push_back(giver.data[ig]);
    taker.sum.push_back(giver.sum[ig]);
    taker.err.push_back(giver.err[ig]);
    for (TString proc: ALL_PROCS) {
        taker.procs[proc.Data()].push_back(giver.procs[proc.Data()][ig]);
    }
    return taker;
}

void write_PlotData_to_file(PlotData pData, std::string filename) {
    std::ofstream ofs(filename.c_str(), std::ios::out | std::ofstream::binary);
    for (uint i=0; i < pData.SR_name.size(); i++) {
        ofs << pData.SR_name[i] << " ";
        ofs << pData.data[i] << " ";
        ofs << pData.sum[i] << " ";
        ofs << pData.err[i] << " ";
        for (TString proc: ALL_PROCS) {
            cout << "write process " << proc.Data() << ", the yield is " << pData.procs[proc.Data()][i] << endl;
            ofs << pData.procs[proc.Data()][i] << " ";
        }
        // for (TString proc: ALL_PROCS) {
        //     ofs << pData.procs_error[proc.Data()][i] << " ";
        // }
        ofs << "\n";
    }
    ofs.close();
}

PlotData read_PlotData_from_file(std::string filename, PlotData pData) {
    std::ifstream ifs(filename.c_str(), std::ios::in | std::ofstream::binary);
    std::string line;
    while (std::getline(ifs, line)) {
        if(line.size() <= 0) break;
        std::vector<std::string> fields = stringSplit(line, " ");
        pData.SR_name.push_back(fields[0]);
        pData.data.push_back(std::stod(fields[1]));
        pData.sum.push_back(std::stod(fields[2]));
        pData.err.push_back(std::stod(fields[3]));
        int proc_idx = 0;
        for (TString proc: ALL_PROCS) {
            pData.procs[proc.Data()].push_back(std::stod(fields[4+proc_idx]));
            proc_idx++;
        }
    }
    return pData;
}

PlotData read_PlotData_from_file(std::string filename) {
    PlotData pData;
    pData = read_PlotData_from_file(filename, pData);
    return pData;
}

PlotData read_PlotData_from_file(std::vector<std::string> filenames) {
    PlotData pData;
    for (std::string fname: filenames) {
        pData = read_PlotData_from_file(fname, pData);
    } 
    return pData;
}

void print_PlotData(PlotData pData) {
    for (TString SR: pData.SR_name) {
        cout << SR << ' ';
    }
    cout << "\n" << endl;
    for (double d: pData.data) {
        cout << d << ' ';
    }
    cout << "\n" << endl;
    for (double d: pData.sum) {
        cout << d << ' ';
    }
    cout << "\n" << endl;
}

PlotData rearrange(PlotData pData, std::map<std::string,TString> ch_map, std::map<std::string,std::string> kin_map = {}, vTStr sr_list = SR_list_2) {
    PlotData pData_arranged;
    int j=0; // index of the arranged PlotData
    if (kin_map.empty()) {
        for (TString SR: sr_list) {
            for (int i=0; i<pData.SR_name.size(); i++) {
                bool sflag = false; // mark for finding a channel inside the current signal region being looped.
                for (TString cat: cat_groups[SR.Data()]) {
                    TString ch_name = ch_map[cat.Data()];
                    if (pData.SR_name[i] == ch_name) sflag = true;
                }
                if (!sflag) continue;
                pData_arranged = assign(pData_arranged, pData, i);
                j++;
            }
        }
        return pData_arranged;
    }
    j=0;
    for (std::string kin: kin_list) {
        for (TString SR: sr_list) {
            for (int i=0; i<pData.SR_name.size(); i++) {
                if (kin_list.size() > 1) { // it's redundent to check the kinematic if there is only one kinematic.
                    if (kin_map[pData.SR_name[i].Data()] != kin) continue;
                }
                bool sflag = false; // mark for finding a channel inside the current signal region being looped.
                for (TString cat: cat_groups[SR.Data()]) {
                    TString ch_name = ch_map[cat.Data()];
                    if (pData.SR_name[i] == ch_name) sflag = true;
                }
                if (!sflag) continue;
                pData_arranged = assign(pData_arranged, pData, i);
                j++;
            }
        }
    }
    return pData_arranged;
}

PlotData rearrange(PlotData pData, std::vector<TString> pName) {  
    PlotData pData_arranged;
    for (TString p: pName) {
        for (int i=0; i<pData.SR_name.size(); i++) {
            if (pData.SR_name[i] == p) {
                pData_arranged = assign(pData_arranged, pData, i);
            }
        }
    }
    return pData_arranged;
}

PlotData aggregateDifferential(PlotData pData) {
    PlotData pData_agg;
    std::vector<double> data_agg = {};
    std::vector<double> sum_agg = {};
    std::vector<double> err_agg = {};
    std::unordered_map<std::string, std::vector<double> > procs_agg;
    for (TString proc: ALL_PROCS) {
        procs_agg[proc.Data()] = {};
    }
    
    double data_tmp = pData.data[0];
    double sum_tmp  = pData.sum[0];
    double err_tmp  = pData.err[0];
    std::unordered_map<std::string, double> procs_tmp;
    for (TString proc: ALL_PROCS) {
        procs_tmp[proc.Data()] = pData.procs[proc.Data()][0];
    }
    
    for (int i=1; i<pData.SR_name.size(); i++) {
        if (pData.SR_name[i] == pData.SR_name[i-1]) {
            data_tmp += pData.data[i];
            sum_tmp  += pData.sum[i];
            err_tmp  += pData.err[i];
            for (TString proc: ALL_PROCS) {
                procs_tmp[proc.Data()] += pData.procs[proc.Data()][i];
            }
        }
        
        if (pData.SR_name[i] != pData.SR_name[i-1])  { // The second term is for the last channel.
            pData_agg.SR_name.push_back(pData.SR_name[i-1]);
            pData_agg.data.push_back(data_tmp);
            pData_agg.sum.push_back(sum_tmp);
            pData_agg.err.push_back(err_tmp);
            for (TString proc: ALL_PROCS) {
                pData_agg.procs[proc.Data()].push_back(procs_tmp[proc.Data()]);
            }
            
            data_tmp = pData.data[i];
            sum_tmp  = pData.sum[i];
            err_tmp  = pData.err[i];
            for (TString proc: ALL_PROCS) {
                procs_tmp[proc.Data()] = pData.procs[proc.Data()][i];
            }
        }
        
        if (i == pData.SR_name.size()-1) {
            if (pData.SR_name[i] == pData.SR_name[i-1]) {
                data_tmp += pData.data[i];
                sum_tmp  += pData.sum[i];
                err_tmp  += pData.err[i];
                for (TString proc: ALL_PROCS) {
                    procs_tmp[proc.Data()] += pData.procs[proc.Data()][i];
                }
            }
            else {
                data_tmp = pData.data[i];
                sum_tmp  = pData.sum[i];
                err_tmp  = pData.err[i];
                for (TString proc: ALL_PROCS) {
                    procs_tmp[proc.Data()] = pData.procs[proc.Data()][i];
                }
            }
            pData_agg.SR_name.push_back(pData.SR_name[i]);
            pData_agg.data.push_back(data_tmp);
            pData_agg.sum.push_back(sum_tmp);
            pData_agg.err.push_back(err_tmp);
            for (TString proc: ALL_PROCS) {
                pData_agg.procs[proc.Data()].push_back(procs_tmp[proc.Data()]);
            }
        }
    }
    return pData_agg;
}

std::vector<PlotData> divide(PlotData pData, std::vector<int> cut_points) {
    std::vector<PlotData> pList = {};
    int istart = 0;
    int iend   = cut_points[0];
    for(int i=0; i<cut_points.size(); i++) {
        PlotData pPart;
        for(int j=istart; j<iend; j++) {
            pPart = assign(pPart, pData, j);
        }
        pList.push_back(pPart);
        if (i<cut_points.size()-1) {
            istart = iend;
            iend  += cut_points[i+1];
        }
    }
    return pList; 
}

PlotData deleteBins(PlotData pData, std::vector<int> indices) {
    PlotData pData_new;
    for (int i=0; i<pData.SR_name.size(); i++) {
        if (std::count(indices.begin(), indices.end(), i)) {
            continue;
        }
        pData_new.SR_name.push_back(pData.SR_name[i]);
        pData_new.data.push_back(pData.data[i]);
        pData_new.sum.push_back(pData.sum[i]);
        pData_new.err.push_back(pData.err[i]);
        for (TString proc: ALL_PROCS) {
            pData_new.procs[proc.Data()].push_back(pData.procs[proc.Data()][i]);
        }
    }
    return pData_new;
}

PlotData removeEmptyBins(PlotData pData) {
    PlotData pData_new;
    std::vector<int> indices = {};
    for (int i=0; i<pData.SR_name.size(); i++) {
        if ((abs(pData.data[i]) < pow(10, -4)) & (abs(pData.sum[i]) < pow(10, -4))) {
            indices.push_back(i);
            //cout << "Adding empty bin: " << i << endl;
        }
    }
    pData_new = deleteBins(pData, indices);
    return pData_new;
    //return pData;
}

std::vector<std::string> all_files(std::string path) {
    DIR *dir; 
    struct dirent *diread;
    std::vector<std::string> files = {};
    
    if ((dir = opendir(path.c_str())) != nullptr) {
        while ((diread = readdir(dir)) != nullptr) {
            std::string file_name = diread->d_name;
            if (file_name[0] != 'S') continue;
            files.push_back(path + file_name);
        }
        closedir (dir);
    }
    else {
        cout << "can't open directory " << path << endl;
    }
    return files;
}

#endif
/* PLOTDATA_H_ */

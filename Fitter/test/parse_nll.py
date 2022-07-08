import ROOT
import os
import numpy as np

#POI_LST = ['cQq13', 'cQq83', 'cQq11', 'ctq1', 'cQq81', 'ctq8', 'ctt1', 'cQQ1', 'cQt8', 'cQt1', 'ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']
POI_LST = ['ctW','ctZ','ctp','cpQM','ctG','cbW','cpQ3','cptb','cpt','cQl3i','cQlMi','cQei','ctli','ctei','ctlSi','ctlTi']

### Helper functions ###

# Get path to root file given base name
#   - Assumes the file is in "../fit_files" relative to where we are
#   - Assumes the file is named higgsCombine{}.MultiDimFit.root
def find_root_file_path(base_name,wc):
    root_file_name = '../fit_files/higgsCombine{}.MultiDimFit.root'.format(base_name+"."+wc)
    if not os.path.exists(root_file_name):
        print("Warning: File {} does not exist.".format(root_file_name))
        return None
    else:
        #print("File {} exists.".format(root_file_name))
        return root_file_name


# Get the values of params from the root file
def get_vals_from_root_file(root_file_path,branches_to_get,srip_poi_branch_names=False):

    # Get scan tree
    ROOT.gROOT.SetBatch(True)
    rootFile = ROOT.TFile.Open(root_file_path)
    limitTree = rootFile.Get('limit')

    # Get coordinates for TGraph
    ret_dict = {}
    for entry in range(limitTree.GetEntries()):
        limitTree.GetEntry(entry)
        for leaf in limitTree.GetListOfLeaves():
            lname = leaf.GetName()
            if lname in branches_to_get:
                keyname = lname
                if srip_poi_branch_names and lname.startswith("trackedParam_"):
                    # Use just the poi name as the key
                    keyname = lname.replace("trackedParam_","")
                if keyname not in ret_dict: ret_dict[keyname] = []
                ret_dict[keyname].append(limitTree.GetLeaf(lname).GetValue(0))

    return ret_dict


# Gets list of branches names
#   - Assumes the non-scanned POIs have the name trackedParam_NAME
#   - Assumes you also want delta NLL
def make_branches_lst(poi_lst,scan_poi):
    out_lst = ["deltaNLL"]
    out_lst.append(scan_poi)
    for poi in poi_lst:
        if poi == scan_poi: continue
        out_lst.append("trackedParam_"+poi)
    return out_lst


# Get arrays that have only one copy of each scan point
#   - Assuming the scan was along scan_var
#   - In case of multiple scan_var values, choose the one with the min minimize_var value
def get_unique_points(in_dict,scan_var,minimize_var):

    # Make sure all of the lists have the same lenght
    ref_len = len(in_dict[scan_var])
    for var_name in in_dict.keys():
        if len(in_dict[var_name]) != ref_len:
            print ref_len, len(in_dict[var_name])
            raise Exception("Error: Something is wrong , not all lists are the same len")

    # Find the index of the unique points we want to keep
    # Put into a dict with this form: {x_val : idx}
    scan_var_val_lst_unique = {}
    for idx in range(ref_len):
        scan_var_val = in_dict[scan_var][idx]
        minimize_var_val = in_dict[minimize_var][idx]
        if scan_var_val not in scan_var_val_lst_unique:
            # This x value is not yet in our unique list
            # So this is necessarilly the best value we've seen for this x value, so put it in the dict
            scan_var_val_lst_unique[scan_var_val] = idx
        else:
            # This x value is already in our unique list
            # We need to decide if the value at this point is better than the one we already have
            idx_of_current_best_minimize_var_val = scan_var_val_lst_unique[scan_var_val]
            current_best_minimize_var_val = in_dict[minimize_var][idx_of_current_best_minimize_var_val]
            if minimize_var_val < current_best_minimize_var_val:
                scan_var_val_lst_unique[scan_var_val] = idx

    # Mask each array, keeping only the elements corresponding to the indices we've selected
    out_dict = {}
    idx_to_keep = scan_var_val_lst_unique.values()
    idx_to_keep.sort()
    idx_to_keep = np.array(idx_to_keep)
    for var_name in in_dict.keys():
        var_val_arr = np.array(in_dict[var_name])
        var_val_arr_unique = np.take(var_val_arr,idx_to_keep)
        out_dict[var_name] = list(var_val_arr_unique)

    return out_dict


### Wrapper functions ###

# Find the best points in EFT space
def get_best_nll_eft_point(in_dict,poi_lst):
    best_point_dict = {}
    best_nll_idx = in_dict["deltaNLL"].index(min(in_dict["deltaNLL"]))
    for poi_name in poi_lst + ["deltaNLL"]:
        poi_val = in_dict[poi_name]
        best_point_dict[poi_name] = in_dict[poi_name][best_nll_idx]

    return best_point_dict

# Take dict like this ctG_scan_dict = {"ctG":1.1,"ctW":2.1}, ctW_scan_dict = {"ctG":1.2,"ctW"2.2} -> ctG_vals=[1.1,1.2] ctW_vals=[2.1,2.2]
def get_best_points_by_wc(lst_of_best_point_dicts):
    best_point_summary = {}
    for poi in POI_LST:
        best_point_summary[poi] = []
    for best_point_dict in lst_of_best_point_dicts:
        for poi in POI_LST:
            best_point_summary[poi].append(best_point_dict[poi])

    return best_point_summary


#####################################
def main():

    #root_file_tag = ".111221.njetsttHbtagSysQuadFixTr2lssp.Frozen"
    #root_file_tag = ".070522.top19001_100pts_realData_randPtsV18_nPointsRand10.njets.1d.Prof"
    root_file_tag = ".052822.top19001_100pts_realData_randPtsV00_nPointsRand10.njets.1d.Prof"
    #root_file_tag = ".070722.top19001_100pts_realData_randPtsV19_nPointsRand00.njets.1d.Prof"

    # Get the best fit from each scan
    best_point_dict_lst = []
    for poi_name in POI_LST:
        print "\n",poi_name
        root_file_name = find_root_file_path(root_file_tag,poi_name)
        branches_to_get = make_branches_lst(POI_LST,poi_name)
        root_dict = get_vals_from_root_file(root_file_name,branches_to_get,True)
        unique_points_dict = get_unique_points(root_dict,poi_name,"deltaNLL")
        best_point = get_best_nll_eft_point(unique_points_dict,POI_LST)
        print best_point
        print best_point["deltaNLL"]
        best_point_dict_lst.append(best_point)

    # Get dictionary of best fit points arranged by WCs
    best_points_by_wc = get_best_points_by_wc(best_point_dict_lst)
    for k,v in best_points_by_wc.items():
        print k,v

    ## Test printing some things
    #variation_extreme_dict = {}
    #for k,v in best_points_by_wc.iteritems():
    #    print k,v
    #    variation_extreme_dict[k] = []
    #    variation_extreme_dict[k].append(min(v))
    #    variation_extreme_dict[k].append(max(v))

    #for k,v in variation_extreme_dict.iteritems():
    #    print k,v

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Note: only works for python3
"""Make the CMSInterferenceFunc scaling input data for the 2lss channels

Download the necessary inputs with:
curl -Ol https://www.crc.nd.edu/~awightma/eft_stuff/for_nick/remade_from_scratch_2023-08-15/withSysts/ttx_multileptons-2lss_p_4j_lj0pt.root
curl -Ol https://www.crc.nd.edu/~awight:ma/eft_stuff/for_nick/remade_from_scratch_2023-08-15/withSysts/ttx_multileptons-2lss_p_5j_lj0pt.root
curl -Ol https://www.crc.nd.edu/~awightma/eft_stuff/for_nick/remade_from_scratch_2023-08-15/withSysts/ttx_multileptons-2lss_p_6j_lj0pt.root
curl -Ol https://www.crc.nd.edu/~awightma/eft_stuff/for_nick/remade_from_scratch_2023-08-15/withSysts/ttx_multileptons-2lss_p_7j_lj0pt.root
curl -Ol https://www.crc.nd.edu/~awightma/eft_stuff/for_nick/remade_from_scratch_2023-08-15/withSysts/combinedcard.txt

Run the command and then build the workspace with:
./makeinterference.py
text2workspace.py combinedcard_sm.txt -P HiggsAnalysis.CombinedLimit.InterferenceModels:interferenceModel --PO scalingData=scalings.json --PO verbose -o workspace-interference.root

To compare with the pre-made workspace, also download
curl -Ol https://www.crc.nd.edu/~awightma/eft_stuff/for_nick/remade_from_scratch_2023-08-15/withSysts/wps.root
and run:
./makeinterference.py compare
This will take a while!
"""

import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import uproot
from matplotlib import pyplot as plt

channels = {
    "ch1": "ttx_multileptons-2lss_p_4j_lj0pt.root",
    "ch2": "ttx_multileptons-2lss_p_5j_lj0pt.root",
    "ch3": "ttx_multileptons-2lss_p_6j_lj0pt.root",
    "ch4": "ttx_multileptons-2lss_p_7j_lj0pt.root",
    "ch5": "ttx_multileptons-2lss_4t_p_4j_lj0pt.root",
    "ch6": "ttx_multileptons-2lss_4t_p_5j_lj0pt.root",
    "ch7": "ttx_multileptons-2lss_4t_p_6j_lj0pt.root",
    "ch8": "ttx_multileptons-2lss_4t_p_7j_lj0pt.root",
    "ch9": "ttx_multileptons-2lss_m_4j_lj0pt.root",
    "ch10": "ttx_multileptons-2lss_m_5j_lj0pt.root",
    "ch11": "ttx_multileptons-2lss_m_6j_lj0pt.root",
    "ch12": "ttx_multileptons-2lss_m_7j_lj0pt.root",
    "ch13": "ttx_multileptons-2lss_p_4j_lj0pt.root",
    "ch14": "ttx_multileptons-2lss_p_6j_lj0pt.root",
    "ch15": "ttx_multileptons-2lss_p_7j_lj0pt.root",
    "ch16": "ttx_multileptons-2lss_p_7j_lj0pt.root",
    "ch17": "ttx_multileptons-3l_m_offZ_1b_2j_lj0pt.root",
    "ch18": "ttx_multileptons-3l_m_offZ_1b_3j_lj0pt.root",
    "ch19": "ttx_multileptons-3l_m_offZ_1b_4j_lj0pt.root",
    "ch20": "ttx_multileptons-3l_m_offZ_1b_5j_lj0pt.root",
    "ch21": "ttx_multileptons-3l_m_offZ_2b_2j_lj0pt.root",
    "ch22": "ttx_multileptons-3l_m_offZ_2b_3j_lj0pt.root",
    "ch23": "ttx_multileptons-3l_m_offZ_2b_4j_lj0pt.root",
    "ch24": "ttx_multileptons-3l_m_offZ_2b_5j_lj0pt.root",
    "ch25": "ttx_multileptons-3l_onZ_1b_2j_ptz.root",
    "ch26": "ttx_multileptons-3l_onZ_1b_3j_ptz.root",
    "ch27": "ttx_multileptons-3l_onZ_1b_4j_ptz.root",
    "ch28": "ttx_multileptons-3l_onZ_1b_5j_ptz.root",
    "ch29": "ttx_multileptons-3l_onZ_2b_2j_lj0pt.root",
    "ch30": "ttx_multileptons-3l_onZ_2b_3j_lj0pt.root",
    "ch31": "ttx_multileptons-3l_onZ_2b_4j_ptz.root",
    "ch32": "ttx_multileptons-3l_onZ_2b_5j_ptz.root",
    "ch33": "ttx_multileptons-3l_p_offZ_1b_2j_lj0pt.root",
    "ch34": "ttx_multileptons-3l_p_offZ_1b_3j_lj0pt.root",
    "ch35": "ttx_multileptons-3l_p_offZ_1b_4j_lj0pt.root",
    "ch36": "ttx_multileptons-3l_p_offZ_1b_5j_lj0pt.root",
    "ch37": "ttx_multileptons-3l_p_offZ_2b_2j_lj0pt.root",
    "ch38": "ttx_multileptons-3l_p_offZ_2b_3j_lj0pt.root",
    "ch39": "ttx_multileptons-3l_p_offZ_2b_4j_lj0pt.root",
    "ch40": "ttx_multileptons-3l_p_offZ_2b_5j_lj0pt.root",
    "ch41": "ttx_multileptons-4l_2j_lj0pt.root",
    "ch42": "ttx_multileptons-4l_3j_lj0pt.root",
    "ch43": "ttx_multileptons-4l_4j_lj0pt.root",
}


eft_procs = [
    "tHq",
    "tllq",
    "ttH",
    "ttll",
    "ttlnu",
    "tttt",
]

all_wcs = [
    "cQQ1",
    "cQei",
    "cQl3i",
    "cQlMi",
    "cQq11",
    "cQq13",
    "cQq81",
    "cQq83",
    "cQt1",
    "cQt8",
    "cbW",
    "cpQ3",
    "cpQM",
    "cpt",
    "cptb",
    "ctG",
    "ctW",
    "ctZ",
    "ctei",
    "ctlSi",
    "ctlTi",
    "ctli",
    "ctp",
    "ctq1",
    "ctq8",
    "ctt1",
]
ncoef = len(all_wcs) + 1  # "cSM"

wc_ranges = {
    "cQQ1": (-6.0, 6.0),
    "cQei": (-4.0, 4.0),
    "cQl3i": (-5.5, 5.5),
    "cQlMi": (-4.0, 4.0),
    "cQq11": (-0.7, 0.7),
    "cQq13": (-0.35, 0.35),
    "cQq81": (-1.7, 1.5),
    "cQq83": (-0.6, 0.6),
    "cQt1": (-6.0, 6.0),
    "cQt8": (-10.0, 10.0),
    "cbW": (-3.0, 3.0),
    "cpQ3": (-4.0, 4.0),
    "cpQM": (-15.0, 20.0),
    "cpt": (-15.0, 15.0),
    "cptb": (-9.0, 9.0),
    "ctG": (-0.8, 0.8),
    "ctW": (-1.5, 1.5),
    "ctZ": (-2.0, 2.0),
    "ctei": (-4.0, 4.0),
    "ctlSi": (-5.0, 5.0),
    "ctlTi": (-0.9, 0.9),
    "ctli": (-4.0, 4.0),
    "ctp": (-15.0, 40.0),
    "ctq1": (-0.6, 0.6),
    "ctq8": (-1.4, 1.4),
    "ctt1": (-2.6, 2.6),
}


def format_wc(wcname):
    lo, hi = wc_ranges[wcname]
    return f"{wcname}[0,{lo:.1f},{hi:.1f}]"


def rewrite_datacard():
    """Rewrites the card removing all non-SM signal processes
    The SM process will then be the one scaled by the CMSInterferenceFunc
    This could be done other ways: e.g. one can scale a non-SM point instead
    The code is very fragile, only meant to work with the 4-channel card from Andrew
    """
    with open("combinedcard.txt") as fin:
        card = list(line.strip() for line in fin)

    procmask = [
        bp == "process" or int(bpi) > 0 or bp.endswith("_sm")
        for bp, bpi in zip(*(line.split() for line in card[53:55]))
    ]

    card[2] = "jmax *"
    for i in range(52, 57):
        card[i] = " ".join(col for mask, col in zip(procmask, card[i].split()) if mask)

    # systname lnN/shape ...
    systmask = [True] + procmask
    for i in range(57, 134):
        card[i] = " ".join(col for mask, col in zip(systmask, card[i].split()) if mask)

    with open("combinedcard_sm.txt", "w") as fout:
        for line in card:
            fout.write(line + "\n")


def make_scaling_json():
    """Read all the input histograms and infer the scaling matrix from
    the various components extracted from the HistEFT object:
        sm piece:    set(c1=0.0)
        a0
        lin piece:   set(c1=1.0)
        a0+a1+b11
        mixed piece: set(c1=1.0,c2=1.0)
        a0+a1+a2+b11+b22+b12
        quad piece:  0.5*[set(c1=2.0) - 2*set(c1=1.0) + set(sm)]
        0.5*(a0+2*a1+4*b11 - 2*a0-2*a1-2*b11 + a0) = b11

    One could go directly from HistEFT to this scaling matrix instead of reversing
    the process to turn it into the separate pieces as done here.
    """
    scalings = []

    print("making scalings.json...")
    for channel, filename in channels.items():
        fin = uproot.open(filename)
        for proc in eft_procs:
            sm = fin[proc + "_sm"].values()
            if np.any(sm <= 0):
                print(f"Negative SM bin yields for {channel} {proc}: {sm}")
                sm = np.where(sm == 0, 10e-25, sm)   # ensure valid divider later
            def getvalues(name):
                if name in fin:
                    out = fin[name].values()
                    if np.any(out < 0):
                        print(f"Example of negative bin yields {name}: {out}")
                    return out

            binscaling = np.zeros((len(sm), ncoef, ncoef))
            binscaling[:, 0, 0] = sm
            for i, wc in enumerate(all_wcs):
                lin = getvalues(f"{proc}_lin_{wc}")
                quad = getvalues(f"{proc}_quad_{wc}")
                if lin is None and quad is None:
                    continue
                ai = lin - quad - sm
                binscaling[:, i + 1, i + 1] = quad
                binscaling[:, 0, i + 1] = ai / 2
                binscaling[:, i + 1, 0] = ai / 2
            for i, wc1 in enumerate(all_wcs):
                lin1 = getvalues(f"{proc}_lin_{wc1}")
                if lin1 is None:
                    continue
                for j, wc2 in enumerate(all_wcs):
                    if j <= i:
                        continue
                    lin2 = getvalues(f"{proc}_lin_{wc2}")
                    if lin2 is None:
                        continue
                    mix = getvalues(f"{proc}_quad_mixed_{wc1}_{wc2}")
                    if mix is None:
                        # try other
                        mix = getvalues(f"{proc}_quad_mixed_{wc2}_{wc1}")
                    if mix is None:
                        raise RuntimeError(f"no mix for {proc}_quad_mixed_{wc2}_{wc1}")
                    # print(i, j, mix)
                    bij = mix - lin1 - lin2 + sm
                    binscaling[:, i + 1, j + 1] = bij / 2
                    binscaling[:, j + 1, i + 1] = bij / 2
            eig, _ = np.linalg.eigh(binscaling)
            print(f"Min eigenvalues for {channel} {proc}: {eig[:, 0]}")
            # divide through by SM yield as that is what will be put in the datacard for the process
            # we could also divide by an arbitrary value, e.g. the yield at a non-SM point in the WC space
            # as long as that same value is put in for the process template
            binscaling /= sm[:, None, None]
            scalings.append(
                {
                    "channel": channel,
                    "process": proc + "_sm",  # NOTE: needs to be in the datacard
                    "parameters": ["cSM[1]"]
                    + [format_wc(wcname) for wcname in all_wcs],
                    "scaling": [
                        list(mat[np.tril_indices(ncoef)]) for mat in binscaling
                    ],
                }
            )

    with open("scalings.json", "w") as fout:
        json.dump(scalings, fout, indent=4)


def run_comparison():
    cmd = (
        "text2workspace.py combinedcard_sm.txt -P HiggsAnalysis.CombinedLimit.InterferenceModels:interferenceModel"
        " --PO scalingData=scalings.json --PO verbose -o workspace-interference.root"
    )
    subprocess.call(cmd.split())
    print("finish workspace making, running fits")
    wcranges = ":".join(f"{wc}={wc_ranges[wc][0]},{wc_ranges[wc][1]}" for wc in all_wcs)

    # whether to fix all other WCs or profile them
    scan = f"--algo grid --floatOtherPOIs 0 --setParameterRanges {wcranges} --points 100"
    # scan = f"--algo grid --floatOtherPOIs 1 --setParameterRanges {wcranges}"

    def runfit(wc):
        tic = time.monotonic()
        cmd = f"combine -M MultiDimFit {scan} -P {wc} ptz-lj0pt_fullR2_anatest25v01_withAutostats_withSys.root -n .scan.{wc}"
        subprocess.call(
            cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
        )
        toc = time.monotonic()
        return toc - tic

    with ThreadPoolExecutor(max_workers=8) as pool:
        tot = sum(pool.map(runfit, all_wcs))

    print(f"Legacy approach: {tot:.1f}s")

    print("running interference fits")
    tic = time.monotonic()
    for wc in all_wcs:
        cmd = f"combine -M MultiDimFit {scan} -P {wc} workspace-interference.root -n .scan.me.{wc}"
        subprocess.call(cmd.split())
    toc = time.monotonic()
    print(f"CMSInterferenceFunc approach: {toc-tic:.1f}s")

    fig, axes = plt.subplots(13, 2, figsize=(8, 13 * 4))

    for wc, ax in zip(all_wcs, axes.reshape(-1)):
        filename = f"higgsCombine.scan.{wc}.MultiDimFit.mH120.root"
        target = uproot.open(filename)["limit"].arrays([wc, "deltaNLL"], entry_start=1)
        filename = f"higgsCombine.scan.me.{wc}.MultiDimFit.mH120.root"
        me = uproot.open(filename)["limit"].arrays([wc, "deltaNLL"], entry_start=1)

        ax.set_title(wc)
        ax.plot(target[wc], target.deltaNLL, label="Target")
        ax.plot(me[wc], me.deltaNLL, label="Me", linestyle="--")
        ax.legend()

    fig.savefig("comparison_26wc_float0.pdf")


if __name__ == "__main__":
    rewrite_datacard()
    make_scaling_json()
    if sys.argv[-1] == "compare":
        run_comparison()
    print("Done")



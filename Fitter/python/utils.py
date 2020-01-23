import re
import os
import subprocess
import logging

# Match strings using one or more regular expressions
def regex_match(lst,regex_lst):
    # NOTE: For the regex_lst patterns, we use the raw string to generate the regular expression.
    #       This means that any regex special characters in the regex_lst should be properly
    #       escaped prior to calling this function.
    # NOTE: The input list is assumed to be a list of str objects and nothing else!
    # TODO: Add whitelist/blacklist option switch
    matches = []
    if len(regex_lst) == 0: return lst[:]
    for s in lst:
        for pat in regex_lst:
            m = re.search(r"%s" % (pat),s)
            if m is not None:
                matches.append(s)
                break
    return matches

# Run a shell subprocess
def run_command(inputs):
    try:
        stdout = subprocess.check_output(inputs,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # Log the error and re-raise the exception
        logging.exception(e)
        logging.error(e.cmd)
        stdout = e.output
        for l in stdout.split('\n'):
            logging.info(l)
        raise e
    for l in stdout.split('\n'):
        logging.info(l)

# Alternate shell subprocess command that pipes subprocess messages to STDOUT
def run_command2(inputs,verbose=True,indent=0):
    # Note: This will hold the main thread and wait for the subprocess to complete
    indent_str = "\t"*indent
    p = subprocess.Popen(inputs,stdout=subprocess.PIPE)
    stdout = []
    while True:
        l = p.stdout.readline()
        if l == '' and p.poll() is not None:
            break
        if l:
            stdout.append(l.strip())
            if verbose: print indent_str+l.strip()
    return stdout

# Returns a list of file names from the target directory, optionally matching a list of regexs
def get_files(tdir,targets=[]):
    if not os.path.exists(tdir): return []
    lst = [x for x in os.listdir(tdir) if os.path.isfile(os.path.join(tdir,x))]
    return regex_match(lst,targets)

# Moves a list of files to the specified target directory
def move_files(files,target):
    width = len(max(files,key=len))
    for src in files:
        dst = os.path.join(target,src)
        os.rename(src,dst)

# Removes files from tdir which match any of the regex in targets list
def clean_dir(tdir,targets,dry_run=False):
    fnames = regex_match(get_files(tdir),targets)
    if len(fnames) == 0: return
    print "Removing files from: {}".format(tdir)
    print "\tTargets: {}".format(targets)
    for fn in fnames:
        fpath = os.path.join(tdir,fn)
        print "\tRemoving {}".format(fn)
        if not dry_run:
            os.remove(fpath)
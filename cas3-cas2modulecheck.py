import os,sys,datetime

def parsemodulelist(modulefile):
    #first import the list from the cas_modules
    line = modulefile.readline()

    moduledict = {}
    while line:
        if line.strip() == "":
            line = modulefile.readline()
            continue;
        else:
            moduleinfo = line.strip().split(',')
            modulename = moduleinfo[0].split('(')[0].strip()
            machinename = moduleinfo[0].split('(')[1].strip(')')
            
            status = moduleinfo[1]
            if len(moduleinfo) == 3:
                version = moduleinfo[2]
                moduledict[machinename] = [modulename,version,status]
            else:
                print modulename+" ( "+machinename+" ) Does not have a version only status: "+ status
                moduledict[machinename] = [modulename,status]

            line = modulefile.readline()

    return moduledict

def main():
    drupalsites='/var/www/html/drupal/sites/'

    if len(sys.argv) > 1:
        site=sys.argv[1]
    else:
        raise SystemExit("You did not supply a site as a parameter")

    print "Parsing CAS2 module list ... "
    print ""
    cas2file = open('cas2_modules.csv','r')
    cas2modules = parsemodulelist(cas2file)
    cas2file.close()
    
    #now time to get the module list for the site that this script is running on
    if not os.path.exists(drupalsites+site):
        #print drupalsites+site + " Does not exis. Exiting"
        raise SystemExit(drupalsites+site + " Does not exis. Exiting")

    os.chdir(drupalsites+site)
    #time for time stamp on exported lists
    nowtime=datetime.datetime.now().strftime('%m%d%y-%H%M')

    print ""
    print ""
    print "Making list for "+site+" in:  "+ drupalsites+site
    os.system('drush pm-list --type=module --format=csv --fields=name,status,version --status=enabled,disabled > /home/dlb213/use_scripts/cas2modulecheck/sites/'+site+'-modules-'+nowtime+'.csv')
    os.chdir('/home/dlb213/use_scripts/cas2modulecheck/sites')
    print "Parsing "+site+"-modules-"+nowtime+".csv ... "
    print ""
    sitemodulefile = open(site+'-modules-'+nowtime+'.csv','r')
    sitemodules = parsemodulelist(sitemodulefile)
    sitemodulefile.close()

    notoncas2=[]
    wrongversion = []

    for mod in sorted(sitemodules):
        if sitemodules[mod][2] == 'Disabled':
            print mod+" is DISABLED please uninstall it before moving the site over"
            if mod not in cas2modules.keys():
                print sitemodules[mod][0] +"( "+mod+" ) Is also not on CAS2, it is ESPECIALLY IMPORTANT you uninstall it"
        elif mod not in cas2modules.keys():
            notoncas2.append( sitemodules[mod][0] +"( "+mod+" )  :  "+sitemodules[mod][1])
        elif mod in cas2modules.keys():
            if sitemodules[mod][1] != cas2modules[mod][1]:
                wrongversion.append(sitemodules[mod][0] +"( "+mod+" )  :  "+sitemodules[mod][1]+" ,  CAS2 Version:  "+cas2modules[mod][1])
            elif len(cas2modules[mod]) != 3:
                print mod + "  On cas2 does not have a version.  This error shouldn't come up"


    #now print out the messages
    print ""
    print "The following modules are not on CAS2:  "
    print "   ------------------------------"
    for message in notoncas2:
        print message
        
    print ""
    print "The Following modules have different versions:"
    print "   ------------------------------"
    for message in wrongversion:
        print message

    print ""

if __name__ == '__main__':
    main()

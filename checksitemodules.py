import os,datetime, sys, argparse

#this script checks a list of supplied modules in csv format to see if those modules are installed on the server
#
# Things to do:
##### integrate command line arguments for
########  checking versions
########  printing out a list of the modules to be used with drush dl, rather than doing it by default

##by default my script will assume that the status is in the file

def parsemodulelist(modulefile,v):
    #set some variables up
    #need to do status too
    if v:
        lnlen = 2
    else:
        lnlen = 1
    modules = {}
    line = modulefile.readline()
    n=1
    while line:
        if line.strip() == "":
            line = modulefile.readline()
            n+=1
            continue
        else:
            linelist = line.split(',')
            if len(linelist)>lnlen and linelist[1].find('(')>0:
                package = linelist[0]
                # Access control,Block Access (block_access),Disabled,7.x-1.6
                # Access control,Block Access (block_access),7.x-1.6
                names = linelist[1].strip().split('(')
                if len(names)>2:
                    #this recreates the module and correctly generates the machine name if there is a parenthesis in the module display name
                    machinename = names[-1].strip(')')
                    modulename = names[0]
                    for chars in names[1:-1]:
                        modulename = modulename + "("+chars

                else:
                    modulename = names[0].strip()
                    machinename = names[1].strip(')')

                #status = linelist[2]

                if v:
                    version = linelist[2].strip()
                    modules[machinename] = [modulename,version,package]
                else:
                    modules[machinename] = [modulename,'--',package]
                #next line
                line = modulefile.readline()
                n+=1
            else:
                print "ERROR READING line "+str(n)+" printing line: "
                print line
                line = modulefile.readline()
                n+=1
                
    return modules
            


def main():
    #setup the arguments for parsing
    #parser=argparse.ArgumentParse()
    #parser.add_argument("version", help="Whether or not the versions should be compared")
    #parser.add_argument("status", help="Whether or not the status should be accepted")
    
    #parser.parse_args()
    
    if len(sys.argv)<2:
        #print 
        raise SystemExit("You must supply a list of modules for this script to work")

    filename=sys.argv[1]
    
    version = False
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('--'):
            if sys.argv[1] == '--version':
                version = True

    here=os.getcwd()
    scripthome="/home/dlb213/usedscripts/newsitemodulecheck"

    now = datetime.datetime.now()
    os.chdir(scripthome)
    os.system('mv currentmodulelist.csv modulelistbackups/currentmodulelist-'+now.strftime('%m%d%y%H%M')+'.csv')

    print "generating current module list"
    os.chdir('/var/www/drupal/sites/')
    os.system('drush pm-list --type=module --format=csv  --fields=package,name,version > /home/dlb213/usedscripts/newsitemodulecheck/currentmodulelist.csv')

    os.chdir(scripthome)
    print "reading in current module list"
    listfile = open('currentmodulelist.csv','r')
    currentlist = parsemodulelist(listfile,version)
    listfile.close()

    os.chdir(here)
    
    print "Reading in file:  "+filename
    modfile=open(filename,'r')
    modulelist = parsemodulelist(modfile,version)
    modfile.close()
    #print "--------------------------------------"
    dlmods=''
    longmodname = 0
    longmachinename = 0
    printlist = []
    for mod in sorted(modulelist):
        if mod not in currentlist.keys():
            #print modulelist[mod][0]+ "      "+mod
            printlist.append((modulelist[mod][0],mod))
            #don't print for now, get the length of the longest string
            if len(modulelist[mod][0])>longmodname:
                longmodname = len(modulelist[mod][0])
            if len(mod) > longmachinename:
                longmachinename = len(mod)
            
            dlmods=mod+','+dlmods

    print '-'.center(longmodname+longmachinename+24,'-')
    for (n,m) in printlist:
        print n.ljust((longmodname+10))+m.ljust((longmachinename+10))

    print '-'.center(longmodname+longmachinename+24,'-')
    #print "--------------------------------------"
    print dlmods.strip(',')
    print ''
    
if __name__ == "__main__":
    main()


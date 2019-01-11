import os,datetime, sys

#this script checks a list of supplied modules in csv format to see if those modules are installed on the server
#
# Things to do:
##### integrate command line arguments for
########  checking versions
########  printing out a list of the modules to be used with drush dl, rather than doing it by default

def parsemodulelist(modulefile,v):
    #set some variables up
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
    os.chdir(here)
    now = datetime.datetime.now()
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
    print "--------------------------------------"
    dlmods=''
    for mod in sorted(modulelist):
        if mod not in currentlist.keys():
            print modulelist[mod][0]+ "      "+mod
            dlmods=mod+','+dlmods
    print "--------------------------------------"
    print dlmods.strip(',')
    print ''
    
if __name__ == "__main__":
    main()


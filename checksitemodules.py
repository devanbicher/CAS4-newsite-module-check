import os,datetime, sys

#This checks the modules on this server and indicates which are missing from the other 2 servers

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
                #Access control,Block Access (block_access),Enabled,7.x-1.6
                #Node export,Node export relation (deprecated) (node_export_relation),Not installed,7.x-3.1
                names = linelist[1].split('(')
                if len(names)>2:
                    #this recreates the module and correctly generates the machine name if there is a parenthesis in the module display name
                    machinename = names[-1].strip(')')
                    modulename = names[0]
                    for chars in names[1:-1]:
                        modulename = modulename + "("+chars

                else:
                    modulename = names[0].strip()
                    machinename = names[1].strip(')')

                status = linelist[2]

                if v:
                    version = linelist[3].strip()
                    modules[machinename] = [modulename,version,status,package]
                else:
                    modules[machinename] = [modulename,'--',status,package]
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

    version = False
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('--'):
            if sys.argv[1] == '--version':
                version = True

    now = datetime.datetime.now()
    os.system('mv currentmodulelist.csv modulelistbackups/currentmodulelist-'+now.strftime('%m%d%y%H%M')+'.csv')
    print "generating current module list"
    os.chdir('/var/www/drupal/sites/')
    os.system('drush pm-list --type=module --format=csv > /home/dlb213/usedscripts/check_installedmodules/currentmodulelist.csv')

    os.chdir(here)
    print "reading in current module list"
    listfile = open('currentmodulelist.csv','r')
    modulelist = parsemodulelist(listfile,version)
    listfile.close()



if __name__ == "__main__":
    main()

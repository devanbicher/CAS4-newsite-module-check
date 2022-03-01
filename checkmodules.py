import sys,os

#usage:
# python checkmodules.py cas2sitelist cas4sitelist

def parsemodulelist(inputfilename):

    moduledict = {}

    inputfile=open(inputfilename,'r')
    inputline = inputfile.readline()
    
    while inputline:
        if inputline.strip() == "":
            inputline = inputfile.readline()
            continue
        elif len(inputline.split(',')) < 3:
            print "Not Enough fields in the module info"
            print inputline
            inputline = inputfile.readline()
            continue
        else:
            moduleinfo=inputline.split(',')
            ##Don't forget some STUPID modules have an extra () in the plain name.  account for that
            if moduleinfo[0].count('(') > 1:
                if moduleinfo[0].count('(') > 2:
                    print "Jeezus, this lack of nameing convention!!"
                    print inputline
                    inputline = inputfile.readline()
                    continue
                
                modulename=moduleinfo[0].split('(')[0] +'('+ moduleinfo[0].split('(')[1]
                machinename=moduleinfo[0].split('(')[2].strip(')')
                
                modulestatus=moduleinfo[1].strip() #probably don't need this
                moduleversion=moduleinfo[2].strip()
            else:
                    #no extra () in the name
                modulename=moduleinfo[0].split('(')[0]
                machinename=moduleinfo[0].split('(')[1].strip(')')
                
                modulestatus=moduleinfo[1].strip() #probably don't need this
                moduleversion=moduleinfo[2].strip()
                
                #append to dictionary

        moduledict[machinename]=[modulename,moduleversion,modulestatus]
        
        inputline = inputfile.readline()

    return moduledict


def main():
    
    if len(sys.argv) < 3:
        print "you did not enter a file for the cas2modules or for cas4modules"
        print "Usage:  python "+sys.argv[0]+" cas2moduleslist.csv cas4moduleslist.csv sitenameDirectory"
        raise SystemExit(5)
    elif len(sys.argv) < 4:
        print "\n ----- !IMPORTANT! ----- "
        print "You did not provide a site folder to copy modules into. So that will not be done, rerun this script with a directory/site name in /var/www/drupal/sites to copy modules from ../keepmodules/ into. \n"
        sitename=''
    else:
        sitename=sys.argv[3]
        
    print "-----------------------"
    print "Checking CAS2 Modules "
    print "-----------------------"
    
    cas2modules = parsemodulelist(sys.argv[1])

    print "-----------------------"
    print "Checking CAS4 Modules "
    print "-----------------------"
    
    cas4modules = parsemodulelist(sys.argv[2])

    greaterversions = []
    lesserversions = []
    otherversions = []
    notinstalled = []
    
    print " --- !NOT INSTALLED MODULES! --- " 
    for module in sorted(cas2modules.keys()):
        if module not in cas4modules.keys():
            print cas2modules[module][0] + " ("+module+"), "+ cas2modules[module][2] +"   NOT INSTALLED "
            notinstalled.append(module)
        elif cas2modules[module][1] != cas4modules[module][1]:
            cas2ver = cas2modules[module][1]
            cas4ver = cas4modules[module][1]
            ver2split = cas2ver.split('-')
            ver4split = cas4ver.split('-')
            
            if len(ver2split) != 2 or len(ver4split) != 2 :
                if len(ver2split) != len(ver4split):
                    otherversions.append(module)
                else:
                    #non stable releases:
                    nonstable = ['dev','alpha','beta','rc']
                    compared=0
                    for n in nonstable:
                        if (n in ver2split[2]) and (n in ver4split[2]):
                            if float(ver4split[2].split(n)[1]) - float(ver2split[2].split(n)[1]) < 0 :
                                lesserversions.append(module)
                            else:
                                greaterversions.append(module)
                                compared=1
                                continue

                    if compared==0 :
                        otherversions.append(module)
                
            else:
                #because 1.10 > 1.9, 1.20 > 1.9, etc we need to check on minor versions if the major version is the same
                if ver2split[1].split('.')[0] != ver4split[1].split('.')[0] :
                    #if the major versions are different, comparison is easy.
                    
                    if float(ver4split[1]) - float(ver2split[1]) < 0 :
                        lesserversions.append(module)
                    else:
                        greaterversions.append(module)
                else:
                    if float(ver4split[1].split('.')[1]) - float(ver2split[1].split('.')[1]) < 0:
                        lesserversions.append(module)
                    else:
                        greaterversions.append(module)
 
            
    #print versions
    print " ------ DIFFERENT VERSIONS! ------ "

    if len(lesserversions) == 0:
        print "\n CAS4 is ahead in all stable module releases "
    else:
        print "\n Cas4 is BEHIND!! : "
        for mod in sorted(lesserversions):
            print cas4modules[mod][0] + "  ("+mod+"), Installed : " +str(cas4modules[mod][1])+ "    CAS2 :  "+ str(cas2modules[mod][1])
            #print module + "  NAME: " + cas4modules[module][0] + "   VERSION: " + cas4modules[module][1] + "  STATUS: "+cas4modules[module][2]

    print "\n Cas4 is AHEAD! : "
    for mod in sorted(greaterversions):
        print cas4modules[mod][0] + "  ("+mod+"), Installed : " +str(cas4modules[mod][1])+ "    CAS2 :  "+ str(cas2modules[mod][1])

    if len(otherversions) == 0 :
        print " \n There are no non-stable releases that can't be compared! "
    else:
        print "\n Dev, beta, alpha, rc or other versions ... "
        for mod in sorted(otherversions):
            print cas4modules[mod][0] + "  ("+mod+"), Installed : " +str(cas4modules[mod][1])+ "    CAS2 :  "+ str(cas2modules[mod][1])
            
    #copy modules from ../keepmodules
    sitespath='/var/www/drupal/sites/'
    if sitename != '' and os.path.exists(sitespath+sitename+"/modules/"):
        #in one line this gets all of the modules that are in the notinstalled list that are also in the keepmodules folder.
        keepmodules = [k for k in os.listdir('../keepmodules/') if k in notinstalled]
        if len(keepmodules) == 0:
            print "There were no modules in ../keepmodules/ that were not installed on this server for this site."
        else:
            print "\n The following modules will be copied into:  "+sitespath+sitename+"/modules/"
            for keep in keepmodules:
                print " - "+keep
            confirm = raw_input("Press y to continue, anything else to exit the script without copying.")
            if confirm == 'y':
                for keep in keepmodules:
                    os.system("cp -r ../keepmodules/"+keep+"/ "+sitespath+sitename+"/modules/")
                os.system("ls -l "+sitespath+sitename+"/modules/")
            else:
                "'y' not detectred, script finished. exiting without copying. you can alwasy rerun this to copy."
            
            
if __name__ == "__main__":
    main()

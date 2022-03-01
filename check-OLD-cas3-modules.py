import os, sys, datetime

def parsemodulelist(moduleslist):

    modules = {}
    line = moduleslist.readline()
    while line:
        if line.strip() == '':
            line = moduleslist.readline()
            continue
        moduleinfo = line.split(',')
        version = moduleinfo[1]
        machinename = moduleinfo[0].split('(')[1].strip(')')
        modulename = moduleinfo[0].split('(')[0]
        status=moduleinfo[2]
        modules[machinename]=[modulename,version,status]

        line = moduleslist.readline()

    return modules


def main():
    #readin the default module list
    defaultfile=open('default-modules.csv','r')
    defaultmodules = parsemodulelist(defaultfile)
    defaultfile.close()
    
    if len(sys.argv) < 2:
        raise SystemExit(" You did not supply a site on which to check the modules")
    
    #now create the other module list
    site=sys.argv[1]
    
    if not os.path.exists('/var/www/html/drupal/sites/'+site):
        raise SystemExit("Oh-oh the site folder you supplied does not exist. try again with a correct site folder.")


    nowtime=datetime.datetime.now().strftime('%m%d%y-%H%M')
    os.chdir('/var/www/html/drupal/sites/'+site)
    os.system('drush pm-list --format=csv --fields=name,version,status --type=module --status=disabled,enabled > /home/dlb213/use_scripts/check-modules/sites/'+site+'-modules-'+nowtime+'.csv')
    os.chdir('/home/dlb213/use_scripts/check-modules/sites/')

    sitefile=open(site+'-modules-'+nowtime+'.csv','r')
    sitemodules=parsemodulelist(sitefile)
    sitefile.close()

    othermodules=open(site+"othermodules-"+nowtime+".csv",'w')
    othermodules.write("Module Name,Machine Name,Version")
    otherhtml=open(site+"-othermodules-"+nowtime+".html",'w');
    otherhtml.write("<p> TABLE BELOW HERE <br><br></p><p><table><tr><th>Module Name</th><th>Machine Name</th><th>Version</th><th>Reason For Installation</th><tr>")

    print "modules Enabled that are NOT in the default site:"

    for mod in sorted(sitemodules):
        if sitemodules[mod][2] == 'Disabled':
            print mod+" is DISABLED. Please uninstall it before proceeding"

        elif mod not in defaultmodules.keys():
            print sitemodules[mod][0]+" ("+mod+")" + " :  "+sitemodules[mod][1]
            othermodules.write(sitemodules[mod][0]+','+mod+','+sitemodules[mod][1]+"\n")
            otherhtml.write('<tr><td>'+sitemodules[mod][0]+'</td><td>'+mod+'</td><td>'+sitemodules[mod][1]+'</td><td></td></tr>')
        elif sitemodules[mod][1] != defaultmodules[mod][1]:
            print sitemodules[mod][1] + " is version "+ sitemodules[mod][1] + "  default is "+defaultmodules[mod][1]
        
    otherhtml.write("</table><p><p><br><br> TABLE ABOVE HERE</p>")
    otherhtml.close()
    othermodules.close()

    if os.path.exists(site+"othermodules-"+nowtime+".csv"):
        os.system('(echo To:dlb213@lehigh.edu; echo From: dlb213@cas-drupal-dev.dept.lehigh.edu; echo "Content-Type: text/html;"; echo Subject: '+site+' Additional modules table; echo; cat '+site+'-othermodules-'+nowtime+'.html ) | sendmail -t')

    print "Email Sent"
    print "------------------------------------------------------"
    print "Modules in the Default Site NOT ENABLED on "+site
    for mod in sorted(defaultmodules):
        if mod not in sitemodules.keys():
            print defaultmodules[mod][0]+" ("+mod+")" + " :  "+defaultmodules[mod][1]
            

if __name__ == "__main__":
    main()

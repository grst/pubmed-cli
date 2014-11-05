package texmedconfig;

# Author: Arne Muller (arne.muller@gmail.com), (c) 2002 - 2012
# texmedconfig.pm part of TeXMed

require Exporter;
@ISA = "Exporter";
@EXPORT_OK = qw($web_view $web_search $web_fetch
                $proxy $user $passwd $tmp $max_fetch
                $max_fetch $tool $email $version $ArticleLinkOut $DbNames);

### Where temporary files will go, note these will *not* get cleaned up!
### You have to setup a cron job to clean up, e.g. the rontab entry below
### runs every day at 6h and 10 min and removes files older than one day;
### 10 6 * * * find /tmp -name 'TeXMed*' -type f -ctime +1 -maxdepth 1 -exec rm -f {} \
$tmp = '/tmp';

### maximum number of hits to retrieve
$max_fetch = 250;

### author/contact email address
$email = 'arne.muller@gmail.com';

$version = '2.0.7, March 2012';

### name of tool
$tool = 'TeXMed';

### ncbi sites for viewing artives as html and the e-utilities ...
$web_view = 'http://www.ncbi.nlm.nih.gov/entrez';
$web_search = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi';
$web_fetch = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi';

### do you need a proxy + authentification? If you use a proxy without
### authentification leave user and passwd empty (remove the passwd code!) ... 
#$proxy  = 'http://proxy.domain.com:2010';
#$user   = 'boo';
#$passwd = '';
#$passwd = `cat ~/.passwd`; # this is a file with the password, mode 600 !!!
#chop($passwd);

### used to link out article ids to online databases
$ArticleLinkOut = {pubmed => 'http://www.ncbi.nlm.nih.gov/pubmed',
                   pmc => 'http://www.ncbi.nlm.nih.gov/pmc/articles',
                   doi => 'http://dx.doi.org'};
### human readable online database names
$DbNames = {pubmed => 'PubMed', pmc => 'PubMed Central', doi => 'DOI'};

return 1;

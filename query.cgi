#!/usr/bin/perl -w
#                              -*- Mode: CPerl -*-

# Author: Arne Muller (arne.muller@gmail.com), (c) 2002 - 2012
# query.cgi part of TeXMed

use CGI qw(:standard);
use LWP::UserAgent;
use entrez;
use texmedconfig qw($proxy $web_view $tmp $max_fetch $email $version);
$| = 1;


### get and process parameters
my $query =  "8692918";


if ( $query ) {
  ### fetch from PubMed
  my $ua = new LWP::UserAgent();
  $ua->proxy(['http'] => $proxy) if ( $proxy );

  my @uids = entrez::get_pmids($ua, $query);
  print b("Received ", scalar(@uids), "references<p>");
  unless ( @uids ) {
    print "<p class=warn>NO references found!</p>\n";
    print end_html();
    exit();
  }
  sleep 1; # avoid NCBI flooding and getting blocked!

  my @refs = entrez::get_references($ua, @uids);
  if ( @refs != @uids ) {
     my $diff = @uids - @refs;
     print "<p class=warn>WARNING: could't fetch entries for $diff referneces!\n</p>";
  }

  print
    start_multipart_form(-target=>'view', -name => 'storeform',
			 action=>'list.cgi'),
      button(-name=>'select all', -onclick=>qq|
              var f = document.getElementsByName('PMID');
              for ( var i=0; i<f.length; i++ ) { f[i].checked = true; }
        |), ' ',
      button(-name=>'un-select all', -onclick=>qq|
              var f = document.getElementsByName('PMID');
	      for ( var i=0; i<f.length; i++ ) { f[i].checked = false;}
        |), ' ',
      hidden(-name=>'action', -value=>'store'),
      hidden(-name=>'session', -value=>$session),
      submit(-value=>'export'),
      checkbox(-name=>'abstract', -label=>" incl. abstract",
               onclick=>'toggleBibLink("abstract", "abstract"); return true;'),
      checkbox(-name=>'linkOut',
               onclick=>'toggleBibLink("linkOut", "linkOut"); return true;',
               -label=> " link article ids (requires \\usepackage{hyperref})"),
      p(),"\n";

  my $entry;
  my $n = 0;

  foreach my $ref ( @refs ) {
     my $uid = $ref->{PMID};
     my $text = summary($ref);
     my $link = a({-href=>"$web_view?Db=pubmed&Cmd=ShowDetailView&uid=$uid",
                   -target=>'view'},
                  $uid);
     $n++;
     my $export = a({-href=>"list.cgi?PMID=$uid", id => "pmid:$uid",
                     -target=>'view', -name => 'bibLink'},
                    'bibtex');
     my $type = join(', ', grep { $_ } @{$ref->{PublicationType}});
     $type = "[ $type ]" if ( $type );
     print "$n. ", checkbox(-name=>'PMID', -value => $uid),
       " $link, $export $type<br>\n$text<p>";
  }
  print end_form;
}

sub summary {
   my $ref = shift;

   my $jrl = $ref->{JournalTitle} ? $ref->{JournalTitle} : 'no journal title';
   my $vol = join(', ', grep { $_ }
                  $ref->{Volume},$ref->{Issue},$ref->{Number});
   my $year =  $ref->{Year} ? $ref->{Year} : 'no year';
   my $title= $ref->{ArticleTitle} ? $ref->{ArticleTitle} : 'no title';
   $title =~ s/\.$//;
   my $auth = join(', ', map { "$ref->{LastName}[$_], $ref->{Initials}[$_]"
                            } 0..@{$ref->{LastName}}-1);
   my $pages = $ref->{Pages} ? $ref->{Pages} : 'np page given';

   return "$auth <b>($year)</b>. $title. <em>$jrl</em>, $vol:$pages.";
}


package entrez;

# Author: Arne Muller (arne.muller@gmail.com), (c) 2002 - 2012
# entrez.pm part of TeXMed

use XML::Parser;
use LWP::UserAgent;
use URI::Escape qw(uri_escape_utf8);
use texmedconfig qw($web_search $web_fetch
                    $proxy $user $passwd $tmp $max_fetch
                    $tool $email);
use strict;
no warnings 'closure'; # needed for the closures (subs withins subs ...)

sub get_pmids {
   my ($ua, $query) = @_;

   return () unless ( $ua && $query );

   ### the commented code does not work if the
   ### query contains utf-8 encoded characters
   ### - no idea why ...!
   #my $req = $ua->request(POST("$web_search",
   #                            [term=>$query,
   #                             retmax=>$max_fetch, retmode=>'XML',
   #                             tool=>$tool, email=>$email])
   #                      );

   ### encoding by hand and passing it directly some how works!
   my $uri_str = "$web_search?term=".uri_escape_utf8($query)
       ."&retmax=$max_fetch&retmode=xml&rettype=full"
       ."&tool=".uri_escape_utf8($tool)
       ."&email=".uri_escape_utf8($email);
   my $req = $ua->post($uri_str);
   $req->content_type('application/x-www-form-urlencoded');
   $req->proxy_authorization_basic($user, $passwd) if ( $user );

   my $code = $req->code();
   if ( !$req->is_success || $req->code != 200 ) {
      warn "get_pmids: '$query' caused HTTP code '$code'\n";
      return();
   }

   my ($idlist, $text) = (0, '');
   my @pmids = ();

   package PMIDS;
   sub IdList { $idlist++ };
   sub IdList_ { $idlist-- };
   sub Id_ {push @pmids, $text if ( $idlist > 0 ) };
   sub baretext {
      $text = $_[1];
      $text =~ s/^\s*(.*?)\s*$/$1/;
   };
   1;

   my $p = new XML::Parser(Style => 'Subs', Pkg => 'PMIDS',
                           Handlers => {Char => \&baretext});
   my $content = $req->content();
   #print "CONTENT:<br>\n";
   #print STDERR "XXXXXX\n$content\nYYYYYYYY\n";
   #$p->parsefile('/home/arne/tmp/test1.xml');
   $p->parsestring($content);
   print STDERR "$content\n";

   return @pmids;
}

sub get_references {
   my ($ua, @pmids) = @_;

   return () unless ( $ua|| @pmids );
   my $ids = join(',', @pmids);

   ### there are problems with the POST implementation, so
   ### I code the URI by hand.
   #my $xreq = $ua->request(POST("$web_fetch",
   #                            [db=>'pubmed', retmode=>'XML', tool=>$tool,
   #                             retmax=>$max_fetch, email=>$email,
   #                             id=>$ids])
   #                      );
   my $uri_str = "$web_fetch?db=pubmed&id="
       .join(",", @pmids)
       ."&retmax=$max_fetch&retmode=xml&rettype=full"
       ."&tool=".uri_escape_utf8($tool)
       ."&email=".uri_escape_utf8($email);

   my $req = $ua->post($uri_str);
   $req->proxy_authorization_basic($user, $passwd) if ( $user );
   my $code = $req->code();

   if ( !$req->is_success || $req->code != 200 ) {
      warn "get_references: '$ids' list caused HTTP code '$code'\n";
      return();
   }
   
   my $curr = 0; # current PubmedArticle
   our @references = (); # array of references (hashes).  'our' so that sub-pkg can use it.
   package REFS;
   sub new_reference {
      return {PMID            => 0,
              Volume          => '',
              Number          => '',
              Year            => '',
              Month           => '',
              Day             => '',
              JournalTitle    => '',
              Pages           => '',
              LastName        => [],
              Initials        => [],
              PublicationType => [],
              ArticleTitle    => '',
              Abstract        => '',
             };
   };
   my ($text, $journal, $articleIdType, $cat) = ('', 0, '', 0);

   sub baretext {
      my $text2 = $_[1];
      $text2 =~ s/\s+/ /g;
      $text = $cat == 1 ? $text. $text2 : $text2; # this is a dirty hack!
   };
   sub PubmedArticle { $curr = new_reference() };
   sub PubmedArticle_ {
     # print "XML::Parse PubmedArticle! PMID:" . $curr->{PMID} . " have " . @references . "\n";
      push @references, $curr;
      $curr = {};
   };
   sub Journal { $journal = 1 };
   sub Journal_ { $journal = 0 };
   sub PMID_ { $curr->{PMID} = $text unless ( $curr->{PMID} )  };
   sub Volume_ { $curr->{Volume} = $text };
   sub Year_ { $curr->{Year} = $text if ( $journal ) };
   sub Month_ { $curr->{Month} = $text if ( $journal ) };
   sub Day_ { $curr->{Day} = $text if ( $journal ) };
   sub Issue_ { $curr->{Number} = $text if ( $journal ) };
   sub MedlineDate_ {
      if ( $journal && !$curr->{Year} ) {
         $curr->{Year} = $1 if ( $text =~ /(\d+)/ );
      }
   };
   sub ISOAbbreviation_ { $curr->{JournalTitle} = $text };
   sub MedlineTA_ { $curr->{JournalTitle} = $text
                      unless ( $curr->{JournalTitle} ) };
   sub MedlinePgn_ { $curr->{Pages} = $text };
   sub LastName_ { push @{$curr->{LastName}}, $text };
   sub Initials_ { push @{$curr->{Initials}}, $text };
   sub PublicationType_ { push @{$curr->{PublicationType}}, $text };
   sub ArticleTitle { $cat = 1 };
   sub ArticleTitle_ { 
     $text =~ s/^\s*(.*?)\s*$/$1/;
     $curr->{ArticleTitle} = $text;
     $cat = 0;
   };
   sub AbstractText { $cat = 1 };
   sub AbstractText_ {
     $text =~ s/^\s*(.*?)\s*$/$1/;
     if ( $curr->{Abstract} ) {
       $curr->{Abstract} = $curr->{Abstract} . '\\\\ ' . $text;
     } else {
       $curr->{Abstract} = $text;
     }
     $cat = 0;
   };
   sub ArticleId {
      my (undef, undef, %attribs) = @_;
      $articleIdType = $attribs{IdType}
   };
   sub ArticleId_ {
      if ( $articleIdType ) {
         $curr->{ArticleIds}{$articleIdType} = $text;
      }
   };
   1;

   my $p = new XML::Parser(Style => 'Subs', Pkg => 'REFS', ErrorContext=> 3,
                           Handlers =>  {Char => \&baretext,
                                         Default => \&baretext});
   #my $p = new XML::Parser(Style => 'Debug');
   my $content = $req->content();
   my $cp = $p->parsestring($content);
   return @references;
}

return 1;

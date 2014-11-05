#!/usr/bin/perl -w
#                              -*- Mode: CPerl -*-

# Author: Arne Muller (arne.muller@gmail.com), (c) 2002 - 2012
# list.cgi part of TeXMed

#use lib './';
use LWP::UserAgent;
use FindBin;
use lib "$FindBin::Bin/../texmed";
use entrez;
use Getopt::Long;
use texmedconfig qw($proxy $user $passwd $tmp $web_view $ArticleLinkOut $DbNames);
$| = 1;

my %table = ( '�' => 'A', '�' => 'A', '�' => 'A', 
              '�' => 'A', '�' => 'A', '�' => 'A',
              '�' => 'C',
              '�' => 'E', '�' => 'E', '�' => 'E', '�' => 'E',
              '�' => 'I', '�' => 'I', '�' => 'I', '�' => 'I',
              '�' => 'N',
              '�' => 'O', '�' => 'O', '�' => 'O', '�' => 'O', '�' => 'O',
              '�' => 'U', '�' => 'U', '�' => 'U', '�' => 'U',
              '�' => 'a', '�' => 'a', '�' => 'a', '�' => 'a',
              '�' => 'a', '�' => 'a',
              '�' => 'c',
              '�' => 'e', '�' => 'e', '�' => 'e', '�' => 'e',
              '�' => 'i', '�' => 'i', '�' => 'i', '�' => 'i',
              '�' => 'n',
              '�' => 'o', '�' => 'o', '�' => 'o', '�' => 'o', '�' => 'o',
              '�' => 'ss',
              '�' => 'u', '�' => 'u', '�' => 'u', '�' => 'u',
              '�' => 'y' );

sub strip_accents {
    my $str = shift;
    $str =~ s/([^\x00-\x7F])/$table{$1} || '?'/ge;
    $str;
}

my $ua = new LWP::UserAgent;

$abstr = 0;
@ids = ();

GetOptions( "ids=s" => \@ids,
	'abstract|a' => \$abstr);
@ids= split(/,/,join(',',@ids));
#use Data::Dumper;
#print Dumper(@ids);
#print $abstr;
#print STDERR "PMIDS: ", join(', ', @ids), "\n";
my @refs = entrez::get_references($ua, @ids);
if ( @refs != @ids) {
   my $diff = @ids- @refs;
   print "<b>WARNING: could't fetch entries for $diff references!\n</b><p>";
}

my ($refsOK, $badUIDs) = exportBibTeX(@refs);

if ( @$badUIDs ) {
   print "<b class=warn>The following entries could not be exported:</b>\n",p();
   foreach my $uid ( @$badUIDs ) {
      my $link = a({-href=>"$web_view?Db=pubmed&Cmd=ShowDetailView&uid=$uid"},
                  $uid);
      print "PMID $link <p>";
   }
   print b("... END OF LIST WITH BAD ENTRIES\n"), hr(), p();
}

foreach my $ref ( @$refsOK ) { print $ref, "\n\n"; }


### functions

sub exportBibTeX {
  my @entries = @_;

  my @badUIDs;
  my @formated;

  #print "ENTRIES = ", scalar(@entries), "<p>\n";

  foreach my $e ( @entries ) {
    ### first check for type of document, only 'Journal Article' is
    ### supported at the moment, but reviews and proceedings are
    ### stored and cited cited as articles
    unless ( $e->{LastName} && $e->{Initials} && $e->{JournalTitle} &&
             $e->{ArticleTitle} && $e->{Year} &&
             @{$e->{LastName}} == @{$e->{Initials}} ) {
       push @badUIDs, $e->{PMID};
       next;
    }
    ### Author
    my @initials = @{$e->{Initials}};
    grep { $_ =~ s/(\w)/$1\. /g; } @initials;
    my $author = join(' and ', map { "$e->{LastName}[$_], $initials[$_]"
                                  } 0..@{$e->{LastName}}-1);
    $author = 'No authors listed' unless ( $author ) ;
    $author = strip_accents($author);
    ### post-process title
    my $title= $e->{ArticleTitle};
    $title =~ s/\.$//;
    $title =~ s/([A-Z])/\{$1\}/g;

    ### Pages, may have to be calculated (123-30 -> 123--130)
    my $pages = $e->{Pages};
    if ( $pages ) {
       my ($first, $last) = $pages =~ /(\d+)-(\d+)/;
       # print STDERR "PAGES $e->{Pages},  = '$first' - '$last'\n";
       if ( $first && $last && $last < $first ) {
          my $newlast = $first;
          my $n = length($last);
          $newlast =~ s/\d{$n}$/$last/;
          ### note, that some page descriptors start with a letter (D123-30)
          $first = "$1$first" if ( $pages =~ /^([^\d])+/ );
          $pages = "$first--$newlast";
       } elsif ( $last && $first ) {
          $pages = "$first--$last";
       }
    }

	#  my $record = "% $e->{PMID} \n"a;
    $short_title = lc((split(/\s+/, $title))[0]);
    $short_title =~ s/\W//gi;
    $bibid = lc((split(/\W+/, $author))[0]) . $e->{Year} . $short_title;
    $record .= qq/\@Article{$bibid},
   Author="$author",
   Title="{$title}",
   Journal="$e->{JournalTitle}",
   Year="$e->{Year}"/;
    ### now add optional records
    my @opts = ();
    push @opts, qq{   Volume="$e->{Volume}"} if $e->{Volume};
    push @opts, qq{   Number="$e->{Number}"} if $e->{Number};
    push @opts, qq{   Pages="$pages"}  if $pages;
    push @opts, qq{   Month="$e->{Month}"} if $e->{Month};
    push @opts, qq/   Abstract={$e->{Abstract}}/ if ($abstr && $e->{Abstract});
    $record .= join ",\n", '', @opts if ( @opts );
    $record .= "\n}";

    # print pre($record), "\n";

    push @formated, $record;
 }

  return (\@formated, \@badUIDs);
}


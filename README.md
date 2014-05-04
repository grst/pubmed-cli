pubmed-cli
==========

This is just a quick and dirty solution to access pubmed via CLI.

How to use
==========

```
perl pubmed.cgi --ids 9783223,8692918
perl pubmed.cgi --ids 9783223 --ids 8692918
```

Other flags
==========

| Option          | Use                  |
| --------------- |:--------------------:|
| --abstract, -a  | toggles the abstract | 


Searching
========

Currently there's no support for searching on pubmed. If you're interested, have a look at `query.cgi`.

License
=======

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

This is based on the original (texmed)[http://www.bioinformatics.org/texmed/] by Arne Muller.

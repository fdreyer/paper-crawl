#!/usr/bin/env python3
#
# by Frederic Dreyer, 2018
#
# script to download a paper on arxiv and rename the tarball in
# something sensible
#
# or alternatively, get the latex/bibtex entry for the biblio

import sys,argparse,wget

parser = argparse.ArgumentParser(description='Get arxiv data.')
parser.add_argument('arxivNumbers', metavar='arxiv numbers', type=str, nargs='+',
                   help='the list of arxiv numbers to process')
parser.add_argument('--pdf', action='store_true',
                    help='get the PDF file')
parser.add_argument('--download', action='store_true',
                    help='download the tarball and rename it')
parser.add_argument('--bibtex', action='store_true',
                    help='get the bibtex entry')
parser.add_argument('--latex', action='store_true',
                    help='get the latex (EU) entry')
parser.add_argument('--latexUS', action='store_true',
                    help='get the latex (US) entry')

args = parser.parse_args()
nfiles=len(args.arxivNumbers)

cite_dic = {}
for arxiv in args.arxivNumbers:
    if args.pdf:
        pdf_url = 'https://arxiv.org/pdf/'+arxiv
        pdf_filename = wget.download(pdf_url, out=arxiv.replace('.','_')+'.pdf')
        print ('\nDownloaded arXiv:%s pdf as %s' % (arxiv,pdf_filename))

    if args.download:
        tar_url = 'https://arxiv.org/e-print/'+arxiv
        tar_filename = wget.download(tar_url, out=arxiv.replace('.','_')+'.tar.gz')
        print ('\nDownloaded arXiv:%s tarball as %s' % (arxiv,tar_filename))

    if args.latex or args.bibtex or args.latexUS:

        from bs4 import BeautifulSoup
        import urllib3
        http = urllib3.PoolManager()
        url='http://inspirehep.net/search?p=find+eprint+'+arxiv
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="lxml")
        # find part containing link to bibtex, latex entries
        refs=soup.find('ul',attrs={'class':'tight_list'})
        refs=refs.contents[1]
        if args.bibtex:
            bibtex=refs.contents[3]
            bibtex_url=bibtex['href']
            response_bibtex = http.request('GET', bibtex_url)
            soup_bibtex = BeautifulSoup(response_bibtex.data, features="lxml")
            bibtex_entry = soup_bibtex.find(attrs={'class':'pagebodystripemiddle'})
            print(bibtex_entry.text)
            # add citation to dic
            if arxiv not in cite_dic:
                for l in bibtex_entry.text.split():
                    if 'article' in l:
                        cite_dic[arxiv]=l.split('article{',1)[1].split(',',1)[0]
                        break

        if args.latexUS:
            latexUS=refs.contents[5]
            latexUS_url=latexUS['href']
            response_latexUS = http.request('GET', latexUS_url)
            soup_latexUS = BeautifulSoup(response_latexUS.data, features="lxml")
            latexUS_entry = soup_latexUS.find(attrs={'class':'pagebodystripemiddle'})
            # replace br tag by proper line break
            print(latexUS_entry.text.replace('\xa0\xa0','\n  '))
            if arxiv not in cite_dic:
                for l in latexUS_entry.text.split():
                    if 'bibitem' in l:
                        cite_dic[arxiv]=l.split('bibitem{',1)[1].split('}',1)[0]
        if args.latex:
            latex=refs.contents[7]
            latex_url=latex['href']
            response_latex = http.request('GET', latex_url)
            soup_latex = BeautifulSoup(response_latex.data, features="lxml")
            latex_entry = soup_latex.find(attrs={'class':'pagebodystripemiddle'})
            # replace br tag by proper line break
            print(latex_entry.text.replace('\xa0\xa0','\n  '))
            if arxiv not in cite_dic:
                for l in latex_entry.text.split():
                    if 'bibitem' in l:
                        cite_dic[arxiv]=l.split('bibitem{',1)[1].split('}',1)[0]


if cite_dic:
    print('====================\nCite as:',','.join(cite_dic.values()))
    

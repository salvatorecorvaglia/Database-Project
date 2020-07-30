export interface PaperInterface {
  'title': string;
  'abstract': string;
  'type_paper': string;
  'isbn'?: string;
  'issn'?: string;
  'publishing_company'?: string;
  'doi'?: string;
  'pages'?: number;
  'site'?: string;
  'created_on': Date;
  'year'?: number;
  'n_citation': number;
  'n_version': number;
  'rating'?: number;
  'eprint'?: string;
  'pdf'?: string;
  'picture'?: string;
  'added_on': Date;
  'mentioned_in': Array<any>;
  'owns_version': Array<any>;
  'correlated_with': Array<any>;
  'have_category': Array<any>;
  'writers'?: string;
}

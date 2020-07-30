import {PaperInterface} from './PaperInterface';

export interface PaperInterfacePagination {
  'papers': Array<PaperInterface>;
  'paginator': {
    'total': number;
    'num_max_pages': number;
    'items_per_page': number;
    'current_page': number;
  };
}

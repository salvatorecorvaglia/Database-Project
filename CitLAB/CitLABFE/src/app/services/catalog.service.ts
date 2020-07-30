import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Router} from '@angular/router';
import {environment} from '../../environments/environment';
import {CookieService} from 'ngx-cookie-service';
import {AuthService} from './auth.service';
import {Observable} from 'rxjs';
import {PaperInterfacePagination} from '../interfaces/PaperInterfacePagination';
import { Client } from 'elasticsearch-browser';
import * as elasticsearch from 'elasticsearch-browser';

@Injectable({
  providedIn: 'root'
})
export class CatalogService {
  private client: Client;

  constructor(private http: HttpClient, private cookieService: CookieService, public router: Router, private auth: AuthService) {
    if (!this.client) {
      this._connect();
    }
  }

  private connect() {
    this.client = new Client({
      host: 'http://localhost:9200',
      log: 'trace'
    });
  }

  private _connect() {
    this.client = new elasticsearch.Client({
      host: 'localhost:9200',
      log: 'trace'
    });
  }

  isAvailable(): any {
    return this.client.ping({
      requestTimeout: Infinity,
      body: 'Welcome!'
    });
  }

  getWhoCite(author): any {
   const query = {
     'size': 10,
     "query": {
       "multi_match" : {
         "query" : author,
         "fields":     ["references","original_references","pdf_text","writers"],
         "type": "phrase"
       }
     },
     "sort": [
       { "n_citation": { "order": "desc" } }
     ]
   };
    return this.client.search({
      index: 'paper',
      body: query,
      //filterPath: ['hits.hits._source']
    });
  }

  searchFullText(fulltext, size, page): any {
    this.launchNCBI(fulltext).subscribe(resp => {
      console.log(resp);
    }, err => {
      console.log(err);
    });
    const queryfulltext = {
      'from': page - 1,
      'size': size,
      'query': {
          'multi_match' : {
            'query':      fulltext,
            'fields':     ['title','abstract', 'writers','publishing_company'],
            'type': 'phrase'
          }
      },
      'sort': [
        { 'n_citation': { 'order': 'desc' } }
      ]
    };
    return this.client.search({
      index: 'paper',
      body: queryfulltext,
      //filterPath: ['hits.hits._source']
    });
  }

  searchForKeywords(fulltext, size, page): any {
    this.launchNCBI(fulltext).subscribe(resp => {
      console.log(resp);
    }, err => {
      console.log(err);
    });
    const querykeywords = {
      'from': page - 1,
      'size': size,
      'query': {
        'multi_match' : {
          'query':      fulltext,
          'fields':     ['title','abstract', 'writers','publishing_company'],
          'type': 'cross_fields'
        }
      },
      'sort': [
        { 'n_citation': { 'order': 'desc' } }
      ]
    };
    return this.client.search({
      index: 'paper',
      body: querykeywords,
      //filterPath: ['hits.hits._source']
    });
  }

  searchAdvanced(obj, size, page): any {
    if (obj.aw) {
      this.launchNCBI(obj.aw).subscribe(resp => {
        console.log(resp);
      }, err => {
        console.log(err);
      });
    }
    if (obj.ap) {
      this.launchNCBI(obj.ap).subscribe(resp => {
        console.log(resp);
      }, err => {
        console.log(err);
      });
    }
    const queryadvanced = this.buildAdvancedQuery(obj, size, page);
    return this.client.search({
      index: 'paper',
      body: queryadvanced,
      //filterPath: ['hits.hits._source']
    });
  }

  buildAdvancedQuery(obj, size, page) {
    const existKey = [];
    Object.keys(obj).forEach((key) => {
      if (obj[key]) {
        existKey.push(key);
      }
    });
    let queryadvanced = null;
    if (!obj.waf) {
      queryadvanced = {
        'size': size,
        'from': page - 1,
        'query': {
          'bool': {
            'must': [
              {
                'bool' : {
                  'must': []
                }
              },
              {
                'range' : {
                  'year': {
                    'gte' : obj.dp1,
                    'lte' : obj.dp2
                  }
                }
              }
            ],
            'must_not' : {
              'multi_match' : {
                'query':      obj.wtw,
                'fields':     [ 'title', 'abstract'],
                'type': 'cross_fields'
              }
            }
          }
        },
        'sort': [
          {
            'n_citation': {
              'order': 'desc'
            }
          }
        ]
      };
      existKey.forEach((value) => {
        switch (value) {
          case 'alw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.alw,
                'fields':     [ 'title', 'abstract'],
                'type': 'cross_fields'
              }
            });
            break;
          }
          case 'ap': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.ap,
                'fields':     [ 'title', 'abstract'],
                'type': 'phrase'
              }
            });
            break;
          }
          case 'aw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.aw,
                'fields':     [ 'title', 'abstract'],
                'type': 'phrase',
                'slop': 100000
              }
            });
            break;
          }
          case 'raw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'match' : {
                'writers': {
                  'query' : obj.raw,
                  "fuzziness": "AUTO"
                }
              }
            });
            break;
          }
          case 'rap': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'match' : {
                'publishing_company': {
                  'query' : obj.rap,
                  "fuzziness": "AUTO"
                }
              }
            });
            break;
          }
          default: {
            break;
          }
        }
      });
    }

    if (obj.waf === 1) {
      queryadvanced = {
        'size': size,
        'from': page - 1,
        'query': {
          'bool': {
            'must': [
              {
                'bool' : {
                  'must': []
                }
              },
              {
                'range' : {
                  'year': {
                    'gte' : obj.dp1,
                    'lte' : obj.dp2
                  }
                }
              }
            ],
            'must_not' : {
              'multi_match' : {
                'query':      obj.wtw,
                'fields':     ['abstract'],
                'type': 'cross_fields'
              }
            }
          }
        },
        'sort': [
          {
            'n_citation': {
              'order': 'desc'
            }
          }
        ]
      };
      existKey.forEach((value) => {
        switch (value) {
          case 'alw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.alw,
                'fields':     ['abstract'],
                'type': 'cross_fields'
              }
            });
            break;
          }
          case 'ap': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.ap,
                'fields':     ['abstract'],
                'type': 'phrase'
              }
            });
            break;
          }
          case 'aw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.aw,
                'fields':     ['abstract'],
                'type': 'phrase',
                'slop': 100000
              }
            });
            break;
          }
          case 'raw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'match' : {
                'writers': {
                  'query' : obj.raw,
                  "fuzziness": "AUTO"
                }
              }
            });
            break;
          }
          case 'rap': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'match' : {
                'publishing_company': {
                  'query' : obj.rap,
                  "fuzziness": "AUTO"
                }
              }
            });
            break;
          }
          default: {
            break;
          }
        }
      });
    }


    if (obj.waf === 2) {
      queryadvanced = {
        'size': size,
        'from': page - 1,
        'query': {
          'bool': {
            'must': [
              {
                'bool' : {
                  'must': []
                }
              },
              {
                'range' : {
                  'year': {
                    'gte' : obj.dp1,
                    'lte' : obj.dp2
                  }
                }
              }
            ],
            'must_not' : {
              'multi_match' : {
                'query':      '',
                'fields':     [ 'title'],
                'type': 'cross_fields'
              }
            }
          }
        },
        'sort': [
          {
            'n_citation': {
              'order': 'desc'
            }
          }
        ]
      };
      existKey.forEach((value) => {
        switch (value) {
          case 'alw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.alw,
                'fields':     [ 'title'],
                'type': 'cross_fields'
              }
            });
            break;
          }
          case 'ap': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.ap,
                'fields':     [ 'title'],
                'type': 'phrase'
              }
            });
            break;
          }
          case 'aw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'multi_match' : {
                'query':      obj.aw,
                'fields':     [ 'title'],
                'type': 'phrase',
                'slop': 100000
              }
            });
            break;
          }
          case 'raw': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'match' : {
                'writers': {
                  'query' : obj.raw,
                  "fuzziness": "AUTO"
                }
              }
            });
            break;
          }
          case 'rap': {
            queryadvanced.query.bool.must[0].bool.must.push({
              'match' : {
                'publishing_company': {
                  'query' : obj.rap,
                  "fuzziness": "AUTO"
                }
              }
            });
            break;
          }
          default: {
            break;
          }
        }
      });
    }
    return queryadvanced;
  }

  launchNCBI(query): Observable<PaperInterfacePagination> {
    console.log(query);
    const headers = {
      'Authorization': String('Token ' + this.auth.getToken()),
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    return this.http.get(environment.url + 'catalog/ncbi/?q=' + query,
      { headers: new HttpHeaders(headers) }) as Observable<PaperInterfacePagination>;
  }

  searchPub(query, page): Observable<PaperInterfacePagination> {
    const headers = {
      'Authorization': String('Token ' + this.auth.getToken()),
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    return this.http.get(environment.url + 'catalog/search/?q=' + query + '&page=' + page,
      { headers: new HttpHeaders(headers) }) as Observable<PaperInterfacePagination>;
  }

  treeDiagram(id): Observable<any> {
    const headers = {
      'Authorization': String('Token ' + this.auth.getToken()),
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    return this.http.get(environment.url + 'catalog/doc-tree/' + id,
      { headers: new HttpHeaders(headers) }) as Observable<any>;
  }
}

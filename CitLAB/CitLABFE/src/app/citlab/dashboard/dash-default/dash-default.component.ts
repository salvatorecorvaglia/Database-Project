import {ChangeDetectorRef, Component, OnInit, ViewEncapsulation} from '@angular/core';
import {Observable} from 'rxjs';
import {AuthService} from '../../../services/auth.service';
import {CatalogService} from '../../../services/catalog.service';
import {PaperInterface} from '../../../interfaces/PaperInterface';
import {PaperInterfacePagination} from '../../../interfaces/PaperInterfacePagination';
import {NgxSpinnerService} from 'ngx-spinner';
import {NgbModal, ModalDismissReasons, NgbDateStruct, NgbCalendar} from '@ng-bootstrap/ng-bootstrap';
import {NgForm} from '@angular/forms';
import * as sw from 'stopword';
import * as Highcharts from 'highcharts';

import HC_exporting from 'highcharts/modules/exporting';
HC_exporting(Highcharts);

import HC_more from 'highcharts/highcharts-more';
HC_more(Highcharts);

import HC_sankey from 'highcharts/modules/sankey';
import HC_depwheel from 'highcharts/modules/dependency-wheel';

HC_sankey(Highcharts);
HC_depwheel(Highcharts);

Highcharts.setOptions({
  title: {
    style: {
      color: 'tomato'
    }
  },
  legend: {
    enabled: false
  }
});

@Component({
  selector: 'app-dash-default',
  templateUrl: './dash-default.component.html',
  encapsulation: ViewEncapsulation.None,
  styleUrls: ['./dash-default.component.scss']
})
export class DashDefaultComponent implements OnInit {
  public docsList: Array<PaperInterface>;
  public flagTree = false;
  public flagTreeWriters = false;
  public flagSearch = false;
  public flagError = false;
  public currentPage = 1;
  public itemsPerPage = 10;
  public total = 0;
  public closeResult = '';
  public titleTree = '';
  public model1: NgbDateStruct;
  public model2: NgbDateStruct;
  public date: {year: number, month: number};
  public textsearch = '';
  public flagButtonAdvancedSearch = true;
  public errorMessage = '';
  public lastTypeSearch = null;
  public lastTextSearch = null;
  public lastAdvancedSearch = {
    alw: '',
    ap: '',
    aw: '',
    dp1: null,
    dp2: null,
    rap: '',
    raw: '',
    waf: '',
    wtw: '',
  };


  data = {
    json: [],
    config: {
      nodeWidth: 350,
      nodeHeight: 200
    }
  };

  isConnected = false;
  status: string;

  HighchartsCited: typeof Highcharts = Highcharts;
  optionsCited: Highcharts.Options = {
    title: {
      text: 'Author cited by other authors'
    },

    series: [{
      keys: ['from', 'to', 'weight'],
      data: [],
      type: 'sankey',
      name: 'Author citated by'
    }]
  };

  HighchartsReferences: typeof Highcharts = Highcharts;
  optionsReferences: Highcharts.Options = {
    title: {
      text: 'Authors cited in the bibliography of the following document'
    },

    series: [{
      keys: ['from', 'to', 'weight'],
      data: [],
      type: 'dependencywheel',
      name: 'Author quotes'
    }]
  };

  public updateFlag = false;
  public flagActivePlot = false;
  public arrayWriterSelect = new Array();
  public finalArrayWriters = new Array();

  constructor(private auth: AuthService, private catalog: CatalogService, private SpinnerService: NgxSpinnerService,
              private modalService: NgbModal, private calendar: NgbCalendar, private cd: ChangeDetectorRef) {
    this.isConnected = false;
  }

  ngOnInit() {
    /*this.catalog.isAvailable().then(() => {
      this.status = 'OK';
      this.isConnected = true;
    }, error => {
      this.status = 'ERROR';
      this.isConnected = false;
      console.error('Server is down', error);
    }).then(() => {
      this.cd.detectChanges();
    });*/
  }

  changeText(event: any) {
    this.textsearch = event.target.value;
    this.currentPage = null;
  }

  compareDate(start, end) {
    this.flagButtonAdvancedSearch = true;
    if (start && end) {
      const startDate = new Date(start.year, start.month, start.day);
      const endDate = new Date(end.year, end.month, end.day);
      if (startDate > endDate) {
        this.errorMessage = 'The start date cannot be greater than the end date.';
        this.flagButtonAdvancedSearch = false;
      }
    }
  }

  selectToday() {
    return {year: new Date().getFullYear(), month: new Date().getMonth(), day: new Date().getDay()};
  }

  searchFullText(text, page) {
    if (text) {
      if (!page) {
        page = 1;
      }
      this.lastTextSearch = text;
      this.lastTypeSearch = 'ft';
      this.SpinnerService.show();
      this.flagSearch = true;
      this.catalog.searchFullText(text, this.itemsPerPage, page).then(response => {
        this.SpinnerService.hide();
        this.flagError = false;
        this.docsList = response.hits.hits;
        this.total = response.hits.total.value;
      }, error => {
        console.error(error);
        this.SpinnerService.hide();
      }).then(() => {
        console.log('Show Docs Completed!');
      });
    }
  }

  searchForKeywords(text, page) {
    if (text) {
      if (!page) {
        page = 1;
      }
      this.lastTextSearch = text;
      this.lastTypeSearch = 'ok';
      this.SpinnerService.show();
      this.flagSearch = true;
      this.catalog.searchForKeywords(this.rmStopWord(text), this.itemsPerPage, page).then(response => {
        this.SpinnerService.hide();
        this.flagError = false;
        this.docsList = response.hits.hits;
        this.total = response.hits.total.value;
      }, error => {
        console.error(error);
        this.SpinnerService.hide();
      }).then(() => {
        console.log('Show Docs Completed!');
      });
    }
  }

  advancedSearch(form: NgForm) {
    const queryobj = {
      alw: this.rmStopWord(form.value.alw),
      ap: this.checkIfExist(form.value.ap),
      aw: this.rmStopWord(form.value.aw),
      dp1: this.checkIfExistDate(form.value.dp1),
      dp2: this.checkIfExistDate(form.value.dp2),
      rap: this.checkIfExist(form.value.rap),
      raw: this.checkIfExist(form.value.raw),
      waf: this.checkIfExist(form.value.waf),
      wtw: this.rmStopWord(form.value.wtw),
    };
    if (queryobj.alw || queryobj.ap || queryobj.aw || queryobj.dp1 || queryobj.dp2 || queryobj.rap || queryobj.raw || queryobj.wtw) {
      this.SpinnerService.show();
      this.currentPage = 1;
      this.lastTypeSearch = 'as';
      this.flagSearch = true;
      this.catalog.searchAdvanced(queryobj, this.itemsPerPage, this.currentPage).then(response => {
        this.SpinnerService.hide();
        this.lastAdvancedSearch = queryobj;
        this.flagError = false;
        this.docsList = response.hits.hits;
        this.total = response.hits.total.value;
      }, error => {
        console.error(error);
        this.SpinnerService.hide();
      }).then(() => {
        console.log('Show Docs Completed!');
      });
    }
    this.modalService.dismissAll();
  }

  paginationSearch(page) {
    if (this.lastTypeSearch === 'ft') {
      this.SpinnerService.show();
      this.flagSearch = true;
      this.catalog.searchFullText(this.lastTextSearch, this.itemsPerPage, (page * this.itemsPerPage) - this.itemsPerPage + 1)
        .then(response => {
          this.SpinnerService.hide();
          this.flagError = false;
          this.docsList = response.hits.hits;
          this.total = response.hits.total.value;
        }, error => {
          console.error(error);
          this.SpinnerService.hide();
        }).then(() => {
        console.log('Show Docs Completed!');
      });
    }
    if (this.lastTypeSearch === 'ok') {
      this.SpinnerService.show();
      this.flagSearch = true;
      this.catalog.searchForKeywords(this.rmStopWord(this.lastTextSearch), this.itemsPerPage, (page * this.itemsPerPage) - this.itemsPerPage)
        .then(response => {
          this.SpinnerService.hide();
          this.flagError = false;
          this.docsList = response.hits.hits;
          this.total = response.hits.total.value;
        }, error => {
          console.error(error);
          this.SpinnerService.hide();
        }).then(() => {
        console.log('Show Docs Completed!');
      });
    }
    if (this.lastTypeSearch === 'as') {
      this.SpinnerService.show();
      const queryobj = {
        alw: this.lastAdvancedSearch.alw,
        ap: this.lastAdvancedSearch.ap,
        aw: this.lastAdvancedSearch.aw,
        dp1: this.lastAdvancedSearch.dp1,
        dp2: this.lastAdvancedSearch.dp2,
        rap: this.lastAdvancedSearch.rap,
        raw: this.lastAdvancedSearch.raw,
        waf: this.lastAdvancedSearch.waf,
        wtw: this.lastAdvancedSearch.wtw,
      };
      this.flagSearch = true;
      this.catalog.searchAdvanced(queryobj, this.itemsPerPage, (this.currentPage * this.itemsPerPage) - this.itemsPerPage + 1).then(response => {
        this.SpinnerService.hide();
        this.flagError = false;
        this.docsList = response.hits.hits;
        this.total = response.hits.total.value;
      }, error => {
        console.error(error);
        this.SpinnerService.hide();
      }).then(() => {
        console.log('Show Docs Completed!');
      });
    }
  }

  /*searchPub(text, page, type) {
      this.catalog.searchPub(obj, page).subscribe(
        (data) => {
          this.SpinnerService.hide();
          this.flagError = false;
          this.docsList = data.papers;
          this.currentPage = data.paginator.current_page;
          this.itemsPerPage = data.paginator.items_per_page;
          this.total = data.paginator.total;
        }, err => {
          this.SpinnerService.hide();
          this.errorMessage = 'A problem has occurred. Try again. If the problem persists, contact the administration.';
          this.flagError = true;
        }
      );
    }
  }*/

  rmStopWord(text) {
    if (text) {
      let keywords = sw.removeStopwords(this.splitMulti(text, [' ', ',', ';', '|']));
      keywords = sw.removeStopwords(keywords, sw.it);
      return keywords.join(' ');
    }
    return '';
  }

  checkIfExist(value) {
    if (value) {
      return value;
    }
    return '';
  }

  checkIfExistDate(date) {
    if (date) {
      return date.year;
    }
    return null;
  }

  checkValue(value) {
    if (!value) {
      return 'Not Present.';
    }
    return value;
  }

  clearFilter() {
    this.lastAdvancedSearch = {
      alw: '',
      ap: '',
      aw: '',
      dp1: null,
      dp2: null,
      rap: '',
      raw: '',
      waf: '',
      wtw: '',
    };
    this.model1 = null;
    this.model2 = null;
  }

  openTree(content, id, title) {
    this.SpinnerService.show();
    this.titleTree = title;
    this.catalog.treeDiagram(id).subscribe((data) => {
      this.flagTree = false;
      this.SpinnerService.hide();
      this.data.json = data;
      this.modalService.open(content, {windowClass: 'modal-tree-class'}).result.then((result) => {
        this.closeResult = `Closed with: ${result}`;
      }, (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      });
    }, err => {
      this.SpinnerService.hide();
      this.errorMessage = 'A problem has occurred. Try again. If the problem persists, contact the administration.';
      this.flagTree = true;
      this.modalService.open(content, {windowClass: 'modal-tree-class'}).result.then((result) => {
        this.closeResult = `Closed with: ${result}`;
      }, (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      });
    });
  }

  checkIfExistIndex(temporaryArray, writer, type) {
    if (type === 'Mention') {
      let rilevatedIndex = null;
      let index = 0;
      temporaryArray.forEach(writertemp => {
        if (writertemp.writer === writer) {
          rilevatedIndex = index;
        }
        index++;
      });
      return rilevatedIndex;
    } else {
      let rilevatedIndex = null;
      let index = 0;
      this.optionsCited.series[0]['data'].forEach(writertemp => {
        if (writertemp[0] === writer) {
          rilevatedIndex = index;
        }
        index++;
      });
      return rilevatedIndex;
    }

  }

  async openTreePlotSelected(author) {
    this.SpinnerService.show();
    this.updateFlag = false;
    this.optionsReferences.series[0]['data'] = [];
    this.optionsCited.series[0]['data'] = [];
    let counter = 0;
    if (author) {
      this.flagActivePlot = true;
      this.finalArrayWriters.forEach(writer => {
        if (writer[0] === author) {
          this.optionsReferences.series[0]['data'].push(writer);
          counter++;
        }
      });
    }

    await this.catalog.getWhoCite(author).then(response => {
      response.hits.hits.forEach((obj) => {
        const arrayWhoCite = obj._source['writers'].split(',').map(s => s.trim());
        arrayWhoCite.forEach((writer) => {
          this.updateFlag = false;
          const index = this.checkIfExistIndex(null, writer, 'Cited');
          if (index || index === 0) {
            this.optionsCited.series[0]['data'][index] = [this.optionsCited.series[0]['data'][index][0],
              this.optionsCited.series[0]['data'][index][1], (this.optionsCited.series[0]['data'][index][2] +1)];
          } else {
            if (writer !== author) {
              this.optionsCited.series[0]['data'].push([writer, author, 1]);
            }
          }
          this.updateFlag = true;
        });
      });
    }, error => {
      this.SpinnerService.hide();
      console.error(error);
    }).then(() => {
      this.SpinnerService.hide();
      console.log('Show Docs Completed!');
    });
    this.updateFlag = true;
    this.SpinnerService.hide();
  }

  openTreeWriters(content, id, title, parentWriters, citatedWriters) {
    this.optionsReferences.series[0]['data'] = [];
    this.optionsCited.series[0]['data'] = [];
    this.flagActivePlot = false;
    this.flagTreeWriters = false;
    this.errorMessage = '';

    this.titleTree = title;
    this.modalService.open(content, {windowClass: 'modal-tree-class'}).result.then((result) => {
      this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
    });

    const arrayParentWriters = parentWriters.split(',').map(s => s.trim());
    this.arrayWriterSelect = arrayParentWriters;

    const citatedWritersArray = new Array();
    if (citatedWriters) {
      try {
        const citatedWritersjson = citatedWriters.replace(/['"]+/g , '').replace('[', '[\n   ').replace('{' , '{\n      ')
          .replace(/authors: /gi , '\"authors\":\"').replace(/, title: /gi , '\",\"title\":\"').replace(/}/gi , '\"}')
          .replace(/\(/gi , '').replace(/\)/gi , '');
        if (JSON.parse(citatedWritersjson).length > 0) {
          JSON.parse(citatedWritersjson).forEach(obj => {
            const writers = obj.authors.replace(', et al' , '');
            const arrayWriters = writers.split(',');
            arrayWriters.forEach(writer => {
              if (writer.trim() !== 'None' && writer && writer.length < 35) {
                let citatedObj = {
                  'writer': null,
                  'count': null
                };
                let index = this.checkIfExistIndex(citatedWritersArray, writer, 'Mention');
                if (index  || index === 0) {
                  citatedWritersArray[index]['count'] = citatedWritersArray[index]['count'] + 1;
                } else {
                  citatedObj.writer = writer.trim();
                  citatedObj.count = 1;
                  citatedWritersArray.push(citatedObj);
                }
              }
            });
          });
        }
        if (citatedWritersArray.length > 0) {
          arrayParentWriters.forEach((citpar) => {
            citatedWritersArray.forEach((citchild) => {
              this.finalArrayWriters.push([citpar, citchild['writer'], citchild['count']]);
                //this.options.series[0]['data'].push([citpar, citchild['writer'], citchild['count']]);
            });
          });
        }
      }
      catch (err) {
        this.flagTreeWriters = true;
        this.errorMessage = 'For this document is not possible to get the chart.';
      }
    }
  }

  openAdvancedSearch(content) {
    this.modalService.open(content, {ariaLabelledBy: 'modal-basic-title', size: 'lg'}).result.then((result) => {
        this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
    });
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }

  splitMulti(str, tokens) {
    if (str) {
      const tempChar = tokens[0]; // We can use the first token as a temporary join character
      for (let i = 1; i < tokens.length; i++) {
        str = str.split(tokens[i]).join(tempChar);
      }
      str = str.split(tempChar);
      return str.filter(item => item);
    }
    return str;
  }
}

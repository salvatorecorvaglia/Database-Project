import {Component, OnInit} from '@angular/core';
import {NgbDropdownConfig} from '@ng-bootstrap/ng-bootstrap';
import {Router} from '@angular/router';
import {AuthService} from '../../../../../services/auth.service';

@Component({
  selector: 'app-nav-right',
  templateUrl: './nav-right.component.html',
  styleUrls: ['./nav-right.component.scss'],
  providers: [NgbDropdownConfig]
})
export class NavRightComponent implements OnInit {

  constructor(public router: Router, public auth: AuthService) { }

  ngOnInit() { }

  logout() {
    this.auth.logout();
    this.router.navigate(['auth/signin-v2']);
  }
}

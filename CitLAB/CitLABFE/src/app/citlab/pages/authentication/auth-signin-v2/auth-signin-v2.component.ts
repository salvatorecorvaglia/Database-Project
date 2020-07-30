import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { AuthService } from 'src/app/services/auth.service';
import { CookieService } from 'ngx-cookie-service';
import { Router } from '@angular/router';
import { first } from 'rxjs/operators'

@Component({
  selector: 'app-auth-signin-v2',
  templateUrl: './auth-signin-v2.component.html',
  styleUrls: ['./auth-signin-v2.component.scss']
})
export class AuthSigninV2Component implements OnInit {
  public flagAuthenticated = false;
  constructor(private auth: AuthService, private cookieService: CookieService, public router: Router) { 
  }

  ngOnInit() {
    if(this.auth.isAuthenticated()){
      this.router.navigate(['dashboard/pubblications-search']);
    }
  }

  login(form: NgForm) {
    if(form.value.email && form.value.password){
        this.auth.login(form.value.email, form.value.password).pipe(first()).subscribe(
          token=>{
            this.auth.setLogged(token['auth_token']);
            this.router.navigate(['dashboard/pubblications-search']);
        },err => this.flagAuthenticated = true
      );
    }
  }
}

import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { Router } from '@angular/router';
import {NgForm} from '@angular/forms';

@Component({
  selector: 'app-auth-signup-v2',
  templateUrl: './auth-signup-v2.component.html',
  styleUrls: ['./auth-signup-v2.component.scss']
})
export class AuthSignupV2Component implements OnInit {
  public flagErrorRegistration = false;
  public errorMessage = '';

  constructor(private auth: AuthService, private router: Router) { }

  ngOnInit() {
    if (this.auth.isAuthenticated()) {
      this.router.navigate(['dashboard/pubblications-search']);
    }
  }

  register(form: NgForm) {
    if (form.value['first_name'] && form.value['last_name'] && form.value['username'] && form.value['email'] && form.value['password']) {
      this.flagErrorRegistration = false;
      if (/^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,16}$/.test(form.value['password'])) {
        this.auth.registration(form).subscribe((data) => {
          this.router.navigate(['auth/signin-v2']);
        }, err => {
          this.errorMessage = 'This email is already registered!';
          this.flagErrorRegistration = true;
        });
      } else {
        this.errorMessage = 'The password requires at least a number and a special character, its length must be between 6 and 16 characters!';
        this.flagErrorRegistration = true;
      }
    } else {
      this.errorMessage = 'Fill in all the fields!';
      this.flagErrorRegistration = true;
    }
  }
}

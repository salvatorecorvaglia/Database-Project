import { Injectable, OnInit } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { CookieService } from 'ngx-cookie-service';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private http: HttpClient, private cookieService: CookieService, public router: Router) {}

  ngOnInit() {}

  setLogged(token) {
    this.cookieService.set('auth-token', token, 3600);
  }

  login(email: string, password: string) {
    return this.http.post(environment.url + 'auth/token/login', { email: email, password: password });
  }

  registration(form) {
    const options = {
      headers: new HttpHeaders().set('Content-Type', 'application/json')
    };

    return this.http.post(environment.url + 'auth/users/', {
      first_name: form.value['first_name'],
      last_name: form.value['last_name'],
      username: form.value['username'],
      personal_phone: '',
      email: form.value['email'],
      password: form.value['password'],
      re_password: form.value['password']
    }, options);
  }

  isAuthenticated(): boolean {
    const token = this.cookieService.get('auth-token');
    if (token) {
      return true;
    }
    return false;
  }

  logout() {
    this.cookieService.set('auth-token', '', -1);
  }

  getToken(): string {
    const token = this.cookieService.get('auth-token');
    if (token) {
      return token;
    }
    this.router.navigate(['auth/signin-v2']);
  }
}

import { Injectable } from '@angular/core';
import { Router, CanActivate } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';
import { CookieService } from 'ngx-cookie-service';

@Injectable()
export class AuthGuardService implements CanActivate {
    constructor(public auth: AuthService, public router: Router, private cookieService: CookieService) { }
    canActivate(): boolean {
        if (this.auth.isAuthenticated()) {
            return true;
        } else {
            this.router.navigate(['auth/signin-v2']);
        }
    }
}

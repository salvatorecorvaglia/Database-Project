import { NgModule } from '@angular/core';
import { Routes, RouterModule, CanActivate } from '@angular/router';
import { AdminComponent } from './theme/layout/admin/admin.component';
import {AuthComponent} from './theme/layout/auth/auth.component';
import { AuthGuardService } from './guards/auth-guard.service';
import { AccessGuardService } from './guards/access-auth-guard.service';

const routes: Routes = [
  {
    path: '',
    component: AdminComponent,
    canActivate: [AuthGuardService],
    children: [
      {
        path: '',
        redirectTo: 'dashboard/pubblications-search',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadChildren: () => import('./citlab/dashboard/dashboard.module').then(module => module.DashboardModule)
      },
      {
        path: 'sample-page',
        loadChildren: () => import('./citlab/pages/sample-page/sample-page.module').then(module => module.SamplePageModule)
      }
    ]
  },
  {
    path: '',
    component: AuthComponent,
    canActivate: [AccessGuardService],
    children: [
      {
        path: 'auth',
        loadChildren: () => import('./citlab/pages/authentication/authentication.module').then(module => module.AuthenticationModule)
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

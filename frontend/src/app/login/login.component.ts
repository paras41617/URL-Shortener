import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  username: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit() {
    const jwtToken = localStorage.getItem('jwt_token');
  
    if (jwtToken) {
      this.router.navigate(['/']);
    }
  }
  
  onSubmit() {
    const loginData = {
      username: this.username,
      password: this.password
    };
    const apiUrl = 'http://127.0.0.1:5000/login';

    this.http.post(apiUrl, loginData)
      .subscribe(
        (response: any) => {
          
          localStorage.setItem('jwt_token', response.jwt_token);

          this.router.navigate(['/']);
        },
        (error) => {
          this.errorMessage = 'Login failed : '+error.error.message;
        }
      );
  }
}

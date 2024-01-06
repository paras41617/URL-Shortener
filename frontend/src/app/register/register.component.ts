import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
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
    const registerData = {
      username: this.username,
      password: this.password
    };
    const apiUrl = 'http://127.0.0.1:5000/register';

    this.http.post(apiUrl, registerData)
      .subscribe(
        (response: any) => {
          
          this.router.navigate(['/login']);
        },
        (error) => {
          this.errorMessage = "Registration failed: " + error.error["message"];
        }
      );
  }
}

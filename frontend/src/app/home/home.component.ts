import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { jwtDecode } from "jwt-decode";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {
  loggedInUser: string = '';
  activeSection: string = 'profile';
  shortURL: string = '';
  shortenedDetails: any;
  errorMessage: string = '';
  errorMessageStats: string = ''
  analyticsData: any[] = [];

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit() {
    this.getHomeData();
  }

  setActiveSection(section: string) {
    this.activeSection = section;
    if (section == "statistics") {
      this.fetchStats();
    }
  }

  logout() {
    const logoutApiUrl = 'http://127.0.0.1:5000/logout';

    const jwtToken = localStorage.getItem('jwt_token');

    if (jwtToken) {
      this.isTokenExpired(jwtToken);
      const headers = { 'Authorization': `Bearer ${jwtToken}` };

      this.http.post(logoutApiUrl, {}, { headers })
        .subscribe(
          (response: any) => {

            localStorage.removeItem('jwt_token');

            this.router.navigate(['/login']);
          },
          (error) => {
          }
        );
    } else {
      console.error('JWT token not found. User not authenticated.');
    }
  }

  getHomeData() {
    const homeApiUrl = 'http://127.0.0.1:5000/';

    const jwtToken = localStorage.getItem('jwt_token');

    if (jwtToken) {
      this.isTokenExpired(jwtToken);
      const headers = { 'Authorization': `Bearer ${jwtToken}` };

      this.http.get(homeApiUrl, { headers })
        .subscribe(
          (response: any) => {
            localStorage.setItem('username', response.message);
            this.loggedInUser = response.message;
          },
          (error) => {
            console.error('Failed to fetch home data:', error);
          }
        );
    } else {
      this.router.navigate(['/login']);
    }
  }

  onSubmit() {
    const data_url = {
      original_url: this.shortURL,
    };
    const jwtToken = localStorage.getItem('jwt_token');
    if (jwtToken) {
      this.isTokenExpired(jwtToken);
      const headers = { 'Authorization': `Bearer ${jwtToken}` };
      const apiUrl = 'http://127.0.0.1:5000/shorten';
      this.http.post(apiUrl, data_url, { headers })
        .subscribe(
          (response: any) => {
            this.shortenedDetails = response;
            this.errorMessage = '';
          },
          (error) => {
            this.errorMessage = 'Failed to shorten URL. Please try again.';
            this.shortenedDetails = null;
          }
        );
    } else {
      this.router.navigate(['/login']);
    }
  }

  isTokenExpired(token: string) {
    const decodedToken: { exp: number } = jwtDecode(token);
    const isExpired = decodedToken.exp * 1000 < Date.now();

    if (isExpired) {
      localStorage.removeItem('jwt_token');
      this.router.navigate(['/login']);
    }
  }

  fetchStats() {
    const statsUrl = 'http://127.0.0.1:5000/analytics';

    const jwtToken = localStorage.getItem('jwt_token');

    if (jwtToken) {
      this.isTokenExpired(jwtToken);
      const headers = { 'Authorization': `Bearer ${jwtToken}` };

      this.http.get(statsUrl, { headers })
        .subscribe(
          (response: any) => {
            this.analyticsData = response.analytics;
            this.errorMessageStats = '';
          },
          (error) => {
            this.errorMessageStats = 'Failed to fetch analytics data. Please try again.';
            this.analyticsData = [];
          }
        );
    } else {
      this.router.navigate(['/login']);
    }
  }
}

/* import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AnomalyService {
  getAnomalies() {
    throw new Error('Method not implemented.');
  }
  private apiUrl = 'http://127.0.0.1:8000/api/anomalies/';

  constructor(private http: HttpClient) {}

  // ✅ Public method - returns Observable
  loadAnomalies(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }
}*/

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AnomalyService {

  private apiUrl = 'http://127.0.0.1:8000/api/anomalies/';

  constructor(private http: HttpClient) {}

  getAnomalies(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }
}

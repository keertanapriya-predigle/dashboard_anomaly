import { TestBed } from '@angular/core/testing';

import { Anomaly } from './anomaly';

describe('Anomaly', () => {
  let service: Anomaly;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Anomaly);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

import {
  Component,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  Inject,
  PLATFORM_ID,
  ViewChild,
  ElementRef
} from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {

  /* ================= DATA ================= */
  anomalies: any[] = [];
  displayedAnomalies: any[] = [];

  /* ================= PAGINATION ================= */
  pageSize = 6;
  currentPage = 0;
  totalPages = 0;
  pages: number[] = [];
  liveMode = true;

  /* ================= UI ================= */
  loading = true;
  error: string | null = null;

  /* ================= SSE ================= */
  private eventSource!: EventSource;

  /* ================= CHARTS ================= */
  @ViewChild('discountChart') discountChartRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('typeChart') typeChartRef!: ElementRef<HTMLCanvasElement>;

  private discountChart?: Chart;
  private typeChart?: Chart;
  private chartsInitialized = false;

  constructor(
    private cdr: ChangeDetectorRef,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  /* ================= LIFECYCLE ================= */
  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    this.initSSE();
  }

  ngOnDestroy(): void {
    if (this.eventSource) this.eventSource.close();
    if (this.discountChart) this.discountChart.destroy();
    if (this.typeChart) this.typeChart.destroy();
  }

  /* ================= SSE ================= */
  private initSSE() {
    this.eventSource = new EventSource(
      'http://127.0.0.1:8000/api/stream/anomalies/'
    );

    this.eventSource.onmessage = (event) => {
      const incoming = JSON.parse(event.data);

      incoming.forEach((a: any) => {
        a.details ??= {
          price: '-',
          final_price: '-',
          discount_pct: '-'
        };
      });

      this.anomalies.unshift(...incoming);

      this.totalPages = Math.ceil(this.anomalies.length / this.pageSize);
      this.pages = Array.from({ length: this.totalPages }, (_, i) => i);

      if (this.liveMode) {
        this.currentPage = 0;
        this.displayedAnomalies = this.anomalies.slice(0, this.pageSize);
      }

      this.loading = false;
      this.error = null;

      /* 🔑 Force DOM render before chart init */
      this.cdr.detectChanges();

      if (!this.chartsInitialized && this.anomalies.length > 0) {
        Promise.resolve().then(() => {
          this.initCharts();
          this.updateCharts();
          this.chartsInitialized = true;
        });
      } else if (this.chartsInitialized) {
        this.updateCharts();
      }
    };

    this.eventSource.onerror = () => {
      this.error = 'Live connection lost';
      this.loading = false;
      this.cdr.detectChanges();
      this.eventSource.close();
    };
  }

  /* ================= CHARTS ================= */
  private initCharts() {
    console.log('🔄 Initializing charts...');

    if (!this.discountChartRef || !this.typeChartRef) {
      console.warn('⏳ Canvas not ready');
      return;
    }

    const dCanvas = this.discountChartRef.nativeElement;
    const tCanvas = this.typeChartRef.nativeElement;

    // Discount Chart
    if (!this.discountChart) {
      this.discountChart = new Chart(dCanvas, {
        type: 'bar',
        data: {
          labels: ['No Data'],
          datasets: [{
            label: 'Discount %',
            data: [0],
            backgroundColor: 'rgba(54, 162, 235, 0.6)'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
      console.log('✅ Discount chart created');
    }

    // Type Chart
    if (!this.typeChart) {
      this.typeChart = new Chart(tCanvas, {
        type: 'pie',
        data: {
          labels: ['No Data'],
          datasets: [{
            data: [1],
            backgroundColor: [
              'rgba(255, 99, 132, 0.6)',
              'rgba(255, 159, 64, 0.6)',
              'rgba(75, 192, 192, 0.6)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
      console.log('✅ Type chart created');
    }
  }

  private updateCharts() {
    if (!this.discountChart || !this.typeChart) return;

    /* -------- Discount chart -------- */
    const discountMap: Record<string, number> = {};
    this.anomalies.forEach(a => {
      const d = a.details?.discount_pct;
      if (d !== '-' && d !== undefined && d !== null) {
        discountMap[d] = (discountMap[d] || 0) + 1;
      }
    });

    this.discountChart.data.labels =
      Object.keys(discountMap).length ? Object.keys(discountMap) : ['No Data'];
    this.discountChart.data.datasets[0].data =
      Object.values(discountMap).length ? Object.values(discountMap) : [1];
    this.discountChart.update('none');

    /* -------- Type chart -------- */
    const typeMap: Record<string, number> = {};
    this.anomalies.forEach(a => {
      const t = a.anomaly_type ?? 'Unknown';
      typeMap[t] = (typeMap[t] || 0) + 1;
    });

    this.typeChart.data.labels = Object.keys(typeMap);
    this.typeChart.data.datasets[0].data = Object.values(typeMap);
    this.typeChart.update('none');
  }

  /* ================= PAGINATION ================= */
  setPage(page: number) {
    if (page < 0 || page >= this.totalPages) return;

    this.currentPage = page;
    this.liveMode = page === 0;

    const start = page * this.pageSize;
    this.displayedAnomalies = this.anomalies.slice(start, start + this.pageSize);
    this.cdr.detectChanges();
  }

  prevPage() { this.setPage(this.currentPage - 1); }
  nextPage() { this.setPage(this.currentPage + 1); }

  trackById(index: number, item: any) {
    return item.id ?? index;
  }
}

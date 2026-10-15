/**
 * charts.js — Dead-simple, guaranteed-to-work chart rendering.
 * No IntersectionObserver, no complexity. Just fetch → draw.
 */

const COLORS  = ['#22c55e','#0d9488','#06b6d4','#f59e0b','#8b5cf6','#f43f5e'];
const DONUT_C = ['#22c55e','#f59e0b','#06b6d4','#f43f5e'];

const TIP = {
  backgroundColor:'rgba(5,46,22,.92)',
  titleColor:'#86efac',
  bodyColor:'#fff',
  borderColor:'rgba(74,222,128,.3)',
  borderWidth:1,
  cornerRadius:10,
  padding:10,
};

/* Make Chart.js global defaults nice */
Chart.defaults.font.family         = "'Inter','Segoe UI',system-ui,sans-serif";
Chart.defaults.font.size           = 12;
Chart.defaults.color               = '#5a7a62';
Chart.defaults.animation.duration  = 900;
Chart.defaults.animation.easing    = 'easeInOutQuart';
Chart.defaults.responsive          = true;
Chart.defaults.maintainAspectRatio = false;

function draw(id, type, labels, values, opts) {
  const canvas = document.getElementById(id);
  if (!canvas) { console.warn('Canvas not found:', id); return; }

  let datasets, extraOpts = {};

  if (type === 'doughnut') {
    datasets = [{
      data: values,
      backgroundColor: DONUT_C,
      borderWidth: 3,
      borderColor: '#fff',
      hoverOffset: 14,
    }];
    extraOpts = {
      cutout: '65%',
      plugins: {
        legend: { display:true, position:'bottom', labels:{ padding:16, usePointStyle:true } },
        tooltip: TIP,
      },
      animation: { animateRotate:true, animateScale:true },
    };
  } else if (type === 'line') {
    datasets = [{
      label: 'kg collected',
      data: values,
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34,197,94,.12)',
      borderWidth: 2.5,
      pointBackgroundColor: '#22c55e',
      pointBorderColor: '#fff',
      pointBorderWidth: 2.5,
      pointRadius: 5,
      pointHoverRadius: 8,
      fill: true,
      tension: 0.42,
    }];
    extraOpts = {
      plugins: { legend:{ display:false }, tooltip:TIP },
      scales: {
        x: { grid:{ display:false }, ticks:{ font:{ weight:'600' } } },
        y: { grid:{ color:'rgba(22,163,74,.09)' }, beginAtZero:true },
      },
    };
  } else {
    /* bar (vertical or horizontal) */
    const isHoriz = opts && opts.indexAxis === 'y';
    datasets = [{
      label: opts && opts.label || 'Value',
      data: values,
      backgroundColor: COLORS,
      borderRadius: 9,
      borderSkipped: false,
    }];
    extraOpts = {
      indexAxis: isHoriz ? 'y' : 'x',
      plugins: { legend:{ display:false }, tooltip:TIP },
      scales: {
        x: isHoriz
          ? { grid:{ color:'rgba(22,163,74,.09)' }, beginAtZero:true }
          : { grid:{ display:false }, ticks:{ font:{ weight:'600' } } },
        y: isHoriz
          ? { grid:{ display:false }, ticks:{ font:{ weight:'600' } } }
          : { grid:{ color:'rgba(22,163,74,.09)' }, beginAtZero:true },
      },
    };
  }

  new Chart(canvas, {
    type,
    data: { labels, datasets },
    options: extraOpts,
  });
}

/* ── Fetch data and draw all 4 charts ── */
fetch('/api/stats')
  .then(function(r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  })
  .then(function(d) {
    draw('chartCategory',  'bar',      d.by_category.labels,      d.by_category.values,      { label:'kg collected' });
    draw('chartComplaints','bar',      d.complaints_by_type.labels,d.complaints_by_type.values,{ indexAxis:'y', label:'Complaints' });
    draw('chartStatus',    'doughnut', d.by_status.labels,         d.by_status.values,         {});
    draw('chartMonthly',   'line',     d.monthly.labels,           d.monthly.values,           {});
  })
  .catch(function(err) {
    console.error('Stats fetch failed:', err);
    document.querySelectorAll('canvas').forEach(function(c) {
      var ctx = c.getContext('2d');
      ctx.fillStyle = '#ef4444';
      ctx.font = '14px Inter';
      ctx.fillText('Failed to load data', 20, 40);
    });
  });

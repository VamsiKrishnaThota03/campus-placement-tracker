/* Render Plotly figures embedded as <script type="application/json" data-chart="elementId">. */
document.addEventListener('DOMContentLoaded', function () {
  const config = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] };
  document.querySelectorAll('script[data-chart]').forEach(function (node) {
    const target = document.getElementById(node.dataset.chart);
    if (!target) return;
    try {
      const figure = JSON.parse(node.textContent);
      target.innerHTML = '';
      Plotly.newPlot(target, figure.data, figure.layout, config);
    } catch (err) {
      target.innerHTML = '<div class="chart-empty text-danger"><i class="bi bi-exclamation-triangle"></i> Could not draw this chart.</div>';
    }
  });
});

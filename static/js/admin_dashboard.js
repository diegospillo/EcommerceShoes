document.addEventListener('DOMContentLoaded', () => {
    const month = document.getElementById('monthFilter');
    const category = document.getElementById('categoryFilter');
    const gender = document.getElementById('genderFilter');

    const ctxCategory = document.getElementById('categoryChart');
    const ctxGender = document.getElementById('genderChart');
    const ctxMonthly = document.getElementById('monthlyChart');
    const ctxSource = document.getElementById('sourceChart');

    let categoryChart, genderChart, monthlyChart, sourceChart;

    function fetchData() {
        const params = new URLSearchParams();
        if (month.value) params.append('month', month.value);
        if (category.value) params.append('category', category.value);
        if (gender.value) params.append('gender', gender.value);
        fetch('/admin/data?' + params.toString())
            .then(r => r.json())
            .then(updateCharts);
    }

    function buildChart(chart, ctx, type, data) {
        if (chart) chart.destroy();
        return new Chart(ctx, {
            type: type,
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Vendite',
                    data: data.data,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    fill: type === 'line' ? false : true
                }]
            },
            options: {maintainAspectRatio: false}
        });
    }

    function updateCharts(data) {
        categoryChart = buildChart(categoryChart, ctxCategory, 'bar', data.category);
        genderChart = buildChart(genderChart, ctxGender, 'pie', data.gender);
        monthlyChart = buildChart(monthlyChart, ctxMonthly, 'line', data.monthly);
        sourceChart = buildChart(sourceChart, ctxSource, 'bar', data.source);

        const tbody = document.querySelector('#heatmapTable tbody');
        const thead = document.querySelector('#heatmapTable thead');
        tbody.innerHTML = '';
        thead.innerHTML = '';
        const hours = [...new Set(data.heatmap.map(h => (h.hour + 2) % 24))].sort((a,b) => a-b);
        thead.innerHTML = '<tr><th>Giorno/Ora</th>' + hours.map(h => `<th>${h}</th>`).join('') + '</tr>';
        const days = [...new Set(data.heatmap.map(h => h.dow))].sort((a,b) => a-b);
        const names = ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'];
        days.forEach(d => {
            const rowCounts = hours.map(h => {
                const f = data.heatmap.find(x => x.dow === d && (x.hour + 2) % 24 === h);
                return f ? f.count : 0;
            });
            const row = '<tr><th>' + names[d] + '</th>' + rowCounts.map(c => `<td>${c}</td>`).join('') + '</tr>';
            tbody.insertAdjacentHTML('beforeend', row);
        });
    }

    month.addEventListener('change', fetchData);
    category.addEventListener('change', fetchData);
    gender.addEventListener('change', fetchData);
    fetchData();
});
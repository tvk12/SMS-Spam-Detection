document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const analyzeBtn = document.getElementById('analyzeBtn');
    const smsInput = document.getElementById('smsInput');
    const resultArea = document.getElementById('result');
    const predictionResult = document.getElementById('predictionResult');
    const predictionDesc = document.getElementById('predictionDesc');
    const loader = document.querySelector('.loader');
    const btnText = document.querySelector('.btn-text');

    // Feedback
    const feedbackSection = document.getElementById('feedbackSection');
    const feedbackYes = document.getElementById('feedbackYes');
    const feedbackNo = document.getElementById('feedbackNo');
    const feedbackThanks = document.getElementById('feedbackThanks');

    // Stats Elements
    const statTotal = document.getElementById('statTotal');
    const statSpam = document.getElementById('statSpam');
    const statHam = document.getElementById('statHam');
    const logsTableBody = document.getElementById('logsTableBody');

    // Auth & Dev
    const devBtn = document.getElementById('devBtn');
    const devModal = document.getElementById('devModal');
    const closeModal = document.querySelector('.close-modal');
    const generateKeyBtn = document.getElementById('generateKeyBtn');
    const apiKeyDisplay = document.getElementById('apiKeyDisplay');
    const apiKeyCode = document.getElementById('apiKeyCode');

    let currentLogId = null;
    let statsChart = null;
    let sessionApiKey = localStorage.getItem('spam_api_key');

    loadStats();

    // Auto-auth for demo
    if (!sessionApiKey) generateApiKey(true);

    // --- Dev Modal ---
    devBtn.addEventListener('click', () => devModal.classList.remove('hidden'));
    closeModal.addEventListener('click', () => devModal.classList.add('hidden'));
    devModal.addEventListener('click', (e) => {
        if (e.target === devModal) devModal.classList.add('hidden');
    });
    generateKeyBtn.addEventListener('click', () => generateApiKey(false));

    async function generateApiKey(silent = false) {
        try {
            const res = await fetch('/auth/generate-key', { method: 'POST' });
            const data = await res.json();
            sessionApiKey = data.api_key;
            localStorage.setItem('spam_api_key', sessionApiKey);
            if (!silent) {
                apiKeyDisplay.classList.remove('hidden');
                apiKeyCode.textContent = sessionApiKey;
            }
        } catch (e) { console.error(e); }
    }
    // -----------------

    analyzeBtn.addEventListener('click', async () => {
        const text = smsInput.value.trim();
        if (!text) return;

        // UI Reset
        analyzeBtn.disabled = true;
        loader.classList.remove('hidden');
        btnText.textContent = 'Processing...';
        resultArea.classList.add('hidden');
        feedbackSection.classList.add('hidden');
        resetFeedbackUI();

        try {
            if (!sessionApiKey) await generateApiKey(true);

            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': sessionApiKey
                },
                body: JSON.stringify({ text: text }),
            });

            if (response.status === 403) {
                await generateApiKey(true);
                return; // fail silently once, user will retry or logic could retry
            }

            const data = await response.json();
            currentLogId = data.log_id;

            showResult(data.prediction);
            loadStats(); // Refresh stats & table

        } catch (error) {
            console.error(error);
            alert('Error analyzing message');
        } finally {
            analyzeBtn.disabled = false;
            loader.classList.add('hidden');
            btnText.textContent = 'Check Message';
        }
    });

    // Feedback
    feedbackYes.addEventListener('click', () => sendFeedback('Correct'));
    feedbackNo.addEventListener('click', () => sendFeedback('Incorrect'));

    async function sendFeedback(type) {
        if (!currentLogId) return;
        try {
            await fetch(`/feedback/${currentLogId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback: type }),
            });
            feedbackSection.classList.add('hidden');
            feedbackThanks.classList.remove('hidden');
            loadStats();
        } catch (e) { console.error(e); }
    }

    // Navigation
    const navLinks = document.querySelectorAll('.nav-links li');
    const views = {
        'Dashboard': document.getElementById('view-dashboard'),
        'Analytics': document.getElementById('view-analytics'),
        'API Access': document.getElementById('view-api'),
        'Settings': document.getElementById('view-settings')
    };

    // New View Elements
    const historyChartCanvas = document.getElementById('historyChart');
    const apiPageKey = document.getElementById('apiPageKey');
    const regenKeyBtn = document.getElementById('regenKeyBtn');
    const clearLogsBtn = document.getElementById('clearLogsBtn');

    // Setup Nav Click
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const viewName = link.textContent.trim();
            switchView(viewName);
        });
    });

    function switchView(name) {
        // UI Active State
        navLinks.forEach(l => l.classList.remove('active'));
        const activeLink = Array.from(navLinks).find(l => l.textContent.trim() === name);
        if (activeLink) activeLink.classList.add('active');

        // Hide all views
        Object.values(views).forEach(v => v.classList.add('hidden'));

        // Show target
        const target = views[name];
        if (target) {
            target.classList.remove('hidden');
            // Trigger specific view loads
            if (name === 'Analytics') loadHistoryStats();
            if (name === 'API Access') updateApiView();
        }
    }

    // --- Analytics View ---
    let historyChart = null;
    async function loadHistoryStats() {
        try {
            const res = await fetch('/stats/history');
            const data = await res.json();
            renderHistoryChart(data);
        } catch (e) { console.error(e); }
    }

    function renderHistoryChart(data) {
        const dates = Object.keys(data);
        const spamData = dates.map(d => data[d]['Spam']);
        const hamData = dates.map(d => data[d]['Ham']);

        const ctx = historyChartCanvas.getContext('2d');
        if (historyChart) historyChart.destroy();

        historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Spam',
                        data: spamData,
                        borderColor: '#EF4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Ham',
                        data: hamData,
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // --- API View ---
    function updateApiView() {
        if (sessionApiKey) {
            apiPageKey.value = sessionApiKey;
            // Update placeholders
            const host = window.location.origin;
            document.querySelectorAll('.key-placeholder').forEach(el => el.textContent = sessionApiKey);
            const codeBlock = document.querySelector('.code-block code');
            if (codeBlock) codeBlock.innerHTML = codeBlock.innerHTML.replace(/{{host}}/g, host);
        }
    }

    if (regenKeyBtn) {
        regenKeyBtn.addEventListener('click', () => generateApiKey(false));
    }

    // --- Settings View ---
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure? This will delete all history.')) return;
            try {
                await fetch('/admin/logs', {
                    method: 'DELETE',
                    headers: { 'x-api-key': sessionApiKey }
                });
                alert('Logs cleared.');
                loadStats(); // refresh dashboard
            } catch (e) { console.error(e); }
        });
    }

    // --- Shared ---
    function showResult(prediction) {
        resultArea.classList.remove('hidden');
        feedbackSection.classList.remove('hidden');
        const icon = resultArea.querySelector('.result-icon');
        const title = document.getElementById('predictionResult');

        // Reset classes
        icon.className = 'result-icon';
        title.className = '';

        if (prediction === 'Spam') {
            title.textContent = 'Warning: Spam Detected';
            title.style.color = 'var(--danger)';
            predictionDesc.textContent = 'Contains patterns typical of spam.';
        } else {
            title.textContent = 'Safe: Legit Message';
            title.style.color = 'var(--success)';
            predictionDesc.textContent = 'No spam indicators found.';
        }
    }

    function resetFeedbackUI() {
        const feedbackBtns = document.querySelector('.feedback-buttons');
        if (feedbackBtns) feedbackBtns.classList.remove('hidden');
        if (feedbackThanks) feedbackThanks.classList.add('hidden');
    }

    async function loadStats() {
        try {
            const res = await fetch('/stats');
            const data = await res.json();

            // Update Stats Cards
            statTotal.textContent = data.total_requests;
            const spam = data.distribution['Spam'] || 0;
            const ham = data.distribution['Ham'] || 0;
            statSpam.textContent = spam;
            statHam.textContent = ham;

            updateChart(spam, ham);
            updateTable(data.recent_logs); // Populate Table
        } catch (e) { console.error(e); }
    }

    function updateTable(logs) {
        logsTableBody.innerHTML = '';
        if (!logs) return;

        logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>#${log.id}</td>
                <td style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${log.text}</td>
                <td><span style="color: ${log.prediction === 'Spam' ? 'var(--danger)' : 'var(--success)'}; font-weight: 500;">${log.prediction}</span></td>
                <td>${new Date(log.timestamp).toLocaleTimeString()}</td>
                <td>${log.user_feedback || '-'}</td>
            `;
            logsTableBody.appendChild(row);
        });
    }

    function updateChart(spam, ham) {
        const ctx = document.getElementById('statsChart').getContext('2d');
        if (statsChart) {
            statsChart.data.datasets[0].data = [spam, ham];
            statsChart.update();
        } else {
            statsChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Spam', 'Ham'],
                    datasets: [{
                        data: [spam, ham],
                        backgroundColor: ['#EF4444', '#10B981'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }
    }
});

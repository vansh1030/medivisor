document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // UI Elements
    const btn = document.getElementById('submit-btn');
    const btnText = btn.querySelector('span');
    const loader = document.getElementById('btn-loader');
    
    // States
    const idleState = document.getElementById('idle-state');
    const activeState = document.getElementById('active-state');
    const riskLabel = document.getElementById('risk-label');
    const riskBar = document.getElementById('risk-bar');
    const treatmentText = document.getElementById('treatment-text');
    const disclaimerText = document.getElementById('disclaimer-text');

    // Loading State
    btn.disabled = true;
    btnText.textContent = "Analyzing...";
    loader.classList.remove('hidden');

    // Collect Data
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();

        if (result.error) {
            alert('Error: ' + result.error);
            resetBtn();
            return;
        }

        // Show Results Area
        idleState.classList.add('hidden');
        activeState.classList.remove('hidden');

        // Update Text
        riskLabel.textContent = `${result.risk} Risk`;
        treatmentText.textContent = result.treatment;
        disclaimerText.textContent = result.disclaimer;

        // Reset styling
        riskLabel.className = 'risk-label';
        riskBar.className = 'risk-bar';

        // Apply dynamic classes (Timeout ensures CSS transition triggers after display block)
        setTimeout(() => {
            const riskLower = result.risk.toLowerCase();
            riskLabel.classList.add(`risk-${riskLower}`);
            riskBar.classList.add(`bg-${riskLower}`);
        }, 50);

    } catch (error) {
        console.error('Error during prediction:', error);
        alert('Failed to connect to the prediction service.');
    } finally {
        resetBtn();
    }

    function resetBtn() {
        btn.disabled = false;
        btnText.textContent = "Analyze Risk";
        loader.classList.add('hidden');
    }
});

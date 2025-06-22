document.addEventListener('DOMContentLoaded', function() {
    // Initialize any necessary JavaScript functionality
    const focusScoreInputs = document.querySelectorAll('input[type="number"][name="focus_score"]');
    
    focusScoreInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 1) this.value = 1;
            if (this.value > 10) this.value = 10;
        });
    });

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Add time tracking functionality
    const timeTrackers = document.querySelectorAll('input[type="number"][name="study_time"]');
    let timerInterval;
    let startTime;

    timeTrackers.forEach(tracker => {
        const startButton = document.createElement('button');
        startButton.textContent = 'Start Timer';
        startButton.classList.add('btn', 'btn-secondary');
        startButton.type = 'button';
        
        const stopButton = document.createElement('button');
        stopButton.textContent = 'Stop Timer';
        stopButton.classList.add('btn', 'btn-danger');
        stopButton.type = 'button';
        stopButton.style.display = 'none';

        tracker.parentNode.insertBefore(startButton, tracker);
        tracker.parentNode.insertBefore(stopButton, tracker.nextSibling);

        startButton.addEventListener('click', function() {
            startTime = Date.now();
            timerInterval = setInterval(() => {
                const elapsed = Math.floor((Date.now() - startTime) / 1000 / 60);
                tracker.value = elapsed;
            }, 1000);
            startButton.style.display = 'none';
            stopButton.style.display = 'inline-block';
        });

        stopButton.addEventListener('click', function() {
            clearInterval(timerInterval);
            startButton.style.display = 'inline-block';
            stopButton.style.display = 'none';
        });
    });
});
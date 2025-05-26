document.addEventListener('DOMContentLoaded', function() {
    const cityInput = document.getElementById('city-input');
    const autocompleteResults = document.getElementById('autocomplete-results');
    const weatherForm = document.getElementById('weather-form');

    // Check if URL has city parameter (from quick access links)
    const urlParams = new URLSearchParams(window.location.search);
    const cityParam = urlParams.get('city');

    if (cityParam) {
        cityInput.value = cityParam;
        weatherForm.submit();
    }

    // Autocomplete functionality
    cityInput.addEventListener('input', function() {
        const query = this.value.trim();

        if (query.length >= 2) {
            fetch(`/city-autocomplete/?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.cities.length > 0) {
                        autocompleteResults.innerHTML = data.cities.map(city =>
                            `<div>${city}</div>`
                        ).join('');
                        autocompleteResults.style.display = 'block';
                    } else {
                        autocompleteResults.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    autocompleteResults.style.display = 'none';
                });
        } else {
            autocompleteResults.style.display = 'none';
        }
    });

    // Handle click on autocomplete result
    autocompleteResults.addEventListener('click', function(e) {
        if (e.target && e.target.nodeName === 'DIV') {
            cityInput.value = e.target.textContent;
            autocompleteResults.style.display = 'none';
        }
    });

    // Hide autocomplete when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== cityInput) {
            autocompleteResults.style.display = 'none';
        }
    });
});
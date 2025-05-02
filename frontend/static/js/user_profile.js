document.addEventListener('DOMContentLoaded', () => {
    // Hämta CSRF-token från formuläret (om det finns)
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
  
    const changeForm = document.getElementById('change-county-form');
    const select = document.getElementById('new_county');
    const countyResponseDiv = document.getElementById('county-response');
  
    async function loadCountiesForProfile() {
      try {
        const res = await fetch("/subscriptions/counties");
        if (!res.ok) throw new Error("Kunde inte hämta län");
        const counties = await res.json();
  
        const addedCounties = new Set();
        select.innerHTML = '<option value="" disabled selected>Välj län</option>';
        Object.entries(counties).forEach(([code, name]) => {
          if (!addedCounties.has(name)) { 
            addedCounties.add(name); 
            const option = document.createElement("option");
            option.value = code;
            option.textContent = name;
            select.appendChild(option);
          }
        });
      } catch (err) {
        countyResponseDiv.innerHTML = `<p class="error">Fel vid laddning av län: ${err.message}</p>`;
      }
    }
  
    changeForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const newCounty = select.value;
      if (!newCounty) {
        countyResponseDiv.innerHTML = `<p class="error">Vänligen välj ett län.</p>`;
        return;
      }
  
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (csrfToken) {
          headers['X-CSRF-Token'] = csrfToken;
        }
        const response = await fetch('/users/profile/update-county', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ county: newCounty })
        });
  
        const data = await response.json();
        if (response.ok) {
          countyResponseDiv.innerHTML = `<p class="success">Län uppdaterat till ${data.county_name}!</p>`;
          document.querySelector('.info-card li:nth-child(3)').innerHTML = `<strong>Län:</strong> ${data.county_name}`;
        } else {
          countyResponseDiv.innerHTML = `<p class="error">Fel: ${data.error || "Okänt fel"}</p>`;
        }
      } catch (error) {
        countyResponseDiv.innerHTML = `<p class="error">Något gick fel: ${error.message}</p>`;
      }
    });
  
      // Hämta element för avsluta prenumeration
    const unsubscribeForm = document.getElementById('unsubscribe-form');
    const unsubscribeResponseDiv = document.getElementById('unsubscribe-response');
  
    unsubscribeForm.addEventListener('submit', async (event) => {
      event.preventDefault();
  
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (csrfToken) {
          headers['X-CSRF-Token'] = csrfToken;
        }
        const response = await fetch('/users/profile/unsubscribe', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({}) // Inget behov av data i body för denna rutt
        });
  
        const data = await response.json();
        if (response.ok) {
          unsubscribeResponseDiv.innerHTML = `<p class="success">${data.message}</p>`;
          // Ladda om sidan efter 1 sekund för att visa icke-prenumerationsläge
          setTimeout(() => window.location.reload(), 1000);
        } else {
          unsubscribeResponseDiv.innerHTML = `<p class="error">Fel: ${data.error || "Okänt fel"}</p>`;
        }
      } catch (error) {
        unsubscribeResponseDiv.innerHTML = `<p class="error">Något gick fel: ${error.message}</p>`;
      }
    });
  
    loadCountiesForProfile();
  });
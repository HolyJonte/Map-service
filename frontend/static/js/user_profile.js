/* user_profile.js

* Hanterar användarens profil och prenumerationer:
* - Laddar län för användarens profil
* - Hanterar ändring av län
* - Hanterar avregistrering från prenumerationer
* - Visar meddelanden för användaren

*/

/* -----------------------------------------------------------------------------------------------
Hämtar län för användarens profil och hanterar ändring av län
--------------------------------------------------------------------------------------------------*/

// Importerar nödvändiga moduler
document.addEventListener('DOMContentLoaded', () => {
    // Hämta CSRF-token från formuläret (om det finns)
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    // Hämta element för ändra län, välj län och svar
    const changeForm = document.getElementById('change-county-form');
    const select = document.getElementById('new_county');
    const countyResponseDiv = document.getElementById('county-response');
  
    // Hämta län för användarens profil
    async function loadCountiesForProfile() {
      try {
        // Hämta län från servern
        const res = await fetch("/subscriptions/counties");
        if (!res.ok) throw new Error("Kunde inte hämta län");
        // Om svaret är okej, konvertera det till JSON
        const counties = await res.json();
  
        // Om det inte finns några län, visa ett meddelande
        const addedCounties = new Set();
        select.innerHTML = '<option value="" disabled selected>Välj län</option>';
        Object.entries(counties).forEach(([code, name]) => {
          if (!addedCounties.has(name)) { 
            // Lägg till länet i listan om det inte redan finns
            addedCounties.add(name); 
            // Skapa ett nytt alternativ för länet
            const option = document.createElement("option");
            option.value = code;
            option.textContent = name;
            // Lägg till alternativet i select-elementet
            select.appendChild(option);
          }
        });
        // Felmeddelande om inga län hittades
      } catch (err) {
        countyResponseDiv.innerHTML = `<p class="error">Fel vid laddning av län: ${err.message}</p>`;
      }
    }
  
    // Hantera ändring av län
    changeForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      // Hämta det valda länet
      const newCounty = select.value;
      if (!newCounty) {
        // Visa felmeddelande om inget län valdes
        countyResponseDiv.innerHTML = `<p class="error">Vänligen välj ett län.</p>`;
        return;
      }

      // Visa laddningsmeddelande
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (csrfToken) {
          headers['X-CSRF-Token'] = csrfToken;
        }
        // Skicka begäran för att ändra län
        const response = await fetch('/users/profile/update-county', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ county: newCounty })
        });
  
        // Om svaret är okej, konvertera det till JSON
        const data = await response.json();
        if (response.ok) {
          // Visa framgångsmeddelande
          countyResponseDiv.innerHTML = `<p class="success">Län uppdaterat till ${data.county_name}!</p>`;
          document.querySelector('.info-card li:nth-child(3)').innerHTML = `<strong>Län:</strong> ${data.county_name}`;
        } else {
          // Visa felmeddelande
          countyResponseDiv.innerHTML = `<p class="error">Fel: ${data.error || "Okänt fel"}</p>`;
        }
      } catch (error) {
        countyResponseDiv.innerHTML = `<p class="error">Något gick fel: ${error.message}</p>`;
      }
    });
  
      // Hämta element för avsluta prenumeration
    const unsubscribeForm = document.getElementById('unsubscribe-form');
    const unsubscribeResponseDiv = document.getElementById('unsubscribe-response');
    // Hantera avregistrering från prenumerationer
    unsubscribeForm.addEventListener('submit', async (event) => {
      event.preventDefault();
  
      // Visa laddningsmeddelande
      try {
        const headers = { 'Content-Type': 'application/json' };
        if (csrfToken) {
          headers['X-CSRF-Token'] = csrfToken;
        }
        // Skicka begäran för att avregistrera användaren
        const response = await fetch('/users/profile/unsubscribe', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({}) // Inget behov av data i body för denna rutt
        });
  
        // Om svaret är okej, konvertera det till JSON
        const data = await response.json();
        if (response.ok) {
          unsubscribeResponseDiv.innerHTML = `<p class="success">${data.message}</p>`;
          // Ladda om sidan efter 1 sekund för att visa icke-prenumerationsläge
          setTimeout(() => window.location.reload(), 1000);
        } else {
          // Visa felmeddelande om något gick fel
          unsubscribeResponseDiv.innerHTML = `<p class="error">Fel: ${data.error || "Okänt fel"}</p>`;
        }
        // Hantera fel vid begäran eller nätverksproblem 
      } catch (error) {
        unsubscribeResponseDiv.innerHTML = `<p class="error">Något gick fel: ${error.message}</p>`;
      }
    });
  
    // Ladda län för användarens profil när sidan laddas
    loadCountiesForProfile();
  });